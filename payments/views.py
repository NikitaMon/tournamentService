from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from tournaments.models import Registration
from .models import Payment
from .services import PaymentService
from .settings import (
    PAYMENT_STATUS_PENDING,
    PAYMENT_STATUS_SUCCEEDED,
    PAYMENT_STATUS_CANCELED
)
import json
import logging

logger = logging.getLogger(__name__)

def create_payment(request, registration_id):
    """
    Создает платеж для регистрации
    """
    registration = get_object_or_404(Registration, id=registration_id)
    
    # Проверяем, не создан ли уже платеж
    if registration.payments.filter(status=PAYMENT_STATUS_PENDING).exists():
        messages.warning(request, 'У вас уже есть активный платеж')
        return redirect('tournaments:registration_detail', registration_id=registration_id)
    
    # Если это GET запрос, показываем страницу с информацией о платеже
    if request.method == 'GET':
        return render(request, 'payments/payment.html', {
            'registration': registration
        })
    
    # Если это POST запрос, создаем платеж
    payment_service = PaymentService()
    amount = registration.tournament.get_current_registration_price()
    try:
        payment = payment_service.create_payment(
            registration=registration,
            amount=amount,
            description=f"Оплата участия в турнире {registration.tournament.title}"
        )
        
        # Сохраняем информацию о платеже
        Payment.objects.create(
            registration=registration,
            payment_id=payment.id,
            amount=amount,
            status=payment.status,
            payment_url=payment.confirmation.confirmation_url
        )
        
        return redirect(payment.confirmation.confirmation_url)
    except Exception as e:
        messages.error(request, f'Ошибка при создании платежа: {str(e)}')
        return redirect('tournaments:registration_detail', registration_id=registration_id)

def payment_success(request):
    """
    Обработка успешного платежа
    """
    # Логируем все параметры запроса для отладки
    logger.info(f"Payment success callback received. GET params: {request.GET}")
    logger.info(f"Payment success callback received. POST params: {request.POST}")
    logger.info(f"Payment success callback received. Body: {request.body}")
    
    # Получаем payment_id из параметров запроса
    payment_id = None
    
    # Пробуем получить payment_id из тела запроса (основной способ для YooKassa)
    if request.body:
        try:
            data = json.loads(request.body)
            logger.info(f"Parsed request body: {data}")
            
            # Проверяем разные возможные форматы данных от YooKassa
            if isinstance(data, dict):
                # Формат уведомления
                if 'object' in data and 'id' in data['object']:
                    payment_id = data['object']['id']
                # Формат возврата
                elif 'payment_id' in data:
                    payment_id = data['payment_id']
                # Альтернативный формат
                elif 'id' in data:
                    payment_id = data['id']
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse request body as JSON: {e}")
    
    # Если не нашли в теле запроса, пробуем GET параметры
    if not payment_id:
        payment_id = request.GET.get('payment_id')
        if payment_id:
            logger.info(f"Found payment_id in GET params: {payment_id}")
    
    # Если не нашли в GET, пробуем POST параметры
    if not payment_id:
        payment_id = request.POST.get('payment_id')
        if payment_id:
            logger.info(f"Found payment_id in POST params: {payment_id}")
    
    if not payment_id:
        logger.error("Could not find payment_id in request")
        messages.error(request, 'Не удалось получить информацию о платеже')
        return redirect('tournaments:index')
    
    logger.info(f"Processing payment with ID: {payment_id}")
    
    payment_service = PaymentService()
    try:
        # Получаем статус платежа из YooKassa
        status = payment_service.get_payment_status(payment_id)
        logger.info(f"Payment status from YooKassa: {status}")
        
        # Находим платеж в нашей базе
        try:
            payment = Payment.objects.get(payment_id=payment_id)
            logger.info(f"Found payment in database: {payment.id}")
        except Payment.DoesNotExist:
            logger.error(f"Payment not found in database: {payment_id}")
            messages.error(request, 'Платеж не найден в базе данных')
            return redirect('tournaments:index')
        
        if status == PAYMENT_STATUS_SUCCEEDED:
            payment.status = status
            payment.save()
            logger.info(f"Payment {payment_id} marked as succeeded")
            messages.success(request, 'Оплата успешно завершена')
        else:
            logger.warning(f"Payment {payment_id} status: {status}")
            messages.warning(request, f'Платеж находится в обработке. Статус: {status}')
            
        return redirect('tournaments:registration_detail', registration_id=payment.registration.id)
    except Exception as e:
        logger.error(f"Error processing payment {payment_id}: {str(e)}")
        messages.error(request, f'Ошибка при проверке статуса платежа: {str(e)}')
        return redirect('tournaments:index')

def payment_cancel(request):
    """
    Обработка отмены платежа
    """
    payment_id = request.GET.get('payment_id')
    if not payment_id:
        messages.error(request, 'Не удалось получить информацию о платеже')
        return redirect('tournaments:index')
    
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        payment.status = PAYMENT_STATUS_CANCELED
        payment.save()
        messages.info(request, 'Платеж отменен')
        return redirect('tournaments:registration_detail', registration_id=payment.registration.id)
    except Payment.DoesNotExist:
        messages.error(request, 'Платеж не найден')
        return redirect('tournaments:index')
