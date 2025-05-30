from yookassa import Configuration, Payment as YooKassaPayment
from .settings import (
    YOOKASSA_SHOP_ID,
    YOOKASSA_SECRET_KEY,
    PAYMENT_RETURN_URL,
    PAYMENT_CANCEL_URL,
    PAYMENT_STATUS_PENDING
)

class PaymentService:
    def __init__(self):
        Configuration.account_id = YOOKASSA_SHOP_ID
        Configuration.secret_key = YOOKASSA_SECRET_KEY

    def create_payment(self, registration, amount, description):
        """
        Создает платеж в ЮKassa
        """
        payment = YooKassaPayment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": PAYMENT_RETURN_URL
            },
            "capture": True,
            "description": description,
            "metadata": {
                "registration_id": registration.id
            }
        })

        return payment

    def get_payment_status(self, payment_id):
        """
        Получает статус платежа из ЮKassa
        """
        payment = YooKassaPayment.find_one(payment_id)
        return payment.status

    def cancel_payment(self, payment_id):
        """
        Отменяет платеж в ЮKassa
        """
        payment = YooKassaPayment.cancel(payment_id)
        return payment.status 