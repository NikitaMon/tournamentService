from datetime import date
from django.http import JsonResponse
from django.shortcuts import render
from django.utils import timezone
from accounts.forms import UnregisteredParticipantForm
from accounts.models import Profile_organizer
# from accounts.forms import UnregisteredParticipantForm
from tournaments.forms import TournamentForm, TournamentRegistrationForm, WeightCategoriesForm
from tournaments.models import Registration, Tournament, TournamentCategory, TournamentCategoryTemplate
# from tournaments.forms import TournamentForm, TournamentForm2, WeightCategoriesForm, TournamentRegistrationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.shortcuts import redirect
from django.db import models
from collections import defaultdict
from django.template.loader import render_to_string

def index(request):
    now = timezone.now()
    tournaments = Tournament.objects.filter(
        registration_deadline__gt=now
    ).order_by('-created_at')
    return render(request, 'index.html', {'tournaments': tournaments})


def latest(request):
    now = timezone.now()
    tournaments = Tournament.objects.filter(
        registration_deadline__lte=now
    ).order_by('-created_at')
    return render(request, 'latest.html', {'tournaments': tournaments})


def myRegistrations(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Получаем все регистрации пользователя
    registrations = Registration.objects.filter(
        models.Q(Profile_user__user=request.user) | 
        models.Q(unregistered_participant__email=request.user.email)
    ).select_related(
        'Tournament',
        'tournament_category',
        'tournament_category__template',
        'Profile_user',
        'unregistered_participant'
    ).order_by(
        'Tournament__tournament_start'
    )
    
    # Разделяем на текущие и прошедшие регистрации
    today = date.today()
    upcoming_regs = []
    past_regs = []
    
    for reg in registrations:
        if reg.Tournament.tournament_start.date() >= today:
            upcoming_regs.append(reg)
        else:
            past_regs.append(reg)
    
    return render(request, 'my_registrations.html', {
        'upcoming_registrations': upcoming_regs,
        'past_registrations': past_regs,
        'today': today
    })

# def cancelRegistration(request, pk):
#     if not request.user.is_authenticated:
#         return JsonResponse({'status': 'error', 'message': 'Требуется авторизация'}, status=403)
    
#     try:
#         registration = Registration.objects.get(
#             models.Q(Profile_user__user=request.user) | 
#             models.Q(unregistered_participant__email=request.user.email),
#             pk=pk,
#         )
        
#         # Проверяем, что регистрацию еще можно отменить
#         if registration.Tournament.registration_deadline.date() < date.today():
#             return JsonResponse({
#                 'status': 'error',
#                 'message': 'Регистрацию нельзя отменить после дедлайна'
#             }, status=400)
        
#         registration.delete()
#         return JsonResponse({'status': 'success'})
    
#     except Registration.DoesNotExist:
#         return JsonResponse({
#             'status': 'error',
#             'message': 'Регистрация не найдена'
#         }, status=404)

@login_required
@permission_required('tournaments.add_tournament', raise_exception=True)
def createTournament(request):
    if request.method == 'POST':
        form = TournamentForm(request.POST, request.FILES)
        weight_form = WeightCategoriesForm(request.POST, categories=TournamentCategoryTemplate.objects.filter(
            id__in=request.POST.getlist('categories')
        ))
        
        if form.is_valid() and weight_form.is_valid():
            # Сохраняем турнир
            tournament = form.save(commit=False)
            tournament.profile_organizer = request.user.profile_organizer
            tournament.save()
            form.save_m2m()  # Сохраняем ManyToMany поля
            
            # Обрабатываем выбранные категории
            selected_category_templates = form.cleaned_data.get('categories', [])
            for template in selected_category_templates:
                # Получаем измененные веса из формы
                weights_field = f'weights_{template.id}'
                weights_input = weight_form.cleaned_data.get(weights_field, '')
                
                if weights_input:
                    try:
                        weights = [int(w.strip()) for w in weights_input.split(',') if w.strip()]
                    except ValueError:
                        weights = template.weight_categories
                else:
                    weights = template.weight_categories
                
                # Получаем выбранные пояса
                belts_field = f'belts_{template.id}'
                selected_belts = weight_form.cleaned_data.get(belts_field, [])
                
                # Определяем, были ли изменены веса
                edited = weights != template.weight_categories
                
                # Создаем категорию турнира
                category = TournamentCategory.objects.create(
                    template=template,
                    weight_categories=weights,
                    belt_levels=selected_belts,
                    edit=edited
                )
                tournament.tournament_categories.add(category)
            
            messages.success(request, 'Турнир успешно создан!')
            return redirect('tournaments:tournament_detail', pk=tournament.pk)
    else:
        form = TournamentForm()
        weight_form = WeightCategoriesForm(categories=[])
    
    return render(request, 'create_tournament.html', {
        'form': form,
        'weight_form': weight_form
    })

def get_categories(request):
    if request.method == 'POST':
        style_ids = request.POST.get('styles', '').split(',')
        try:
            style_ids = [int(id) for id in style_ids if id]
            categories = TournamentCategoryTemplate.objects.filter(fighting_style__id__in=style_ids)
            
            # Рендерим HTML для списка категорий
            categories_html = render_to_string('partials/categories_checkboxes.html', {
                'categories': categories
            })
            
            # Создаем форму для весовых категорий
            weight_form = WeightCategoriesForm(categories=categories)
            weights_html = render_to_string('partials/weights_form.html', {
                'weight_form': weight_form
            })
            
            return JsonResponse({
                'categories_html': categories_html,
                'weights_html': weights_html
            })
        except ValueError:
            return JsonResponse({'error': 'Invalid input'}, status=400)
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


def get_weights_form(request):
    if request.method == 'POST':
        category_ids = request.POST.get('categories', '').split(',')
        try:
            category_ids = [int(id) for id in category_ids if id]
            categories = TournamentCategoryTemplate.objects.filter(id__in=category_ids)
            
            weight_form = WeightCategoriesForm(categories=categories)
            weights_html = render_to_string('partials/weights_form.html', {
                'weight_form': weight_form
            })
            
            return JsonResponse({
                'status': 'success',
                'weights_html': weights_html
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            }, status=400)
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    }, status=400)


def tournament_detail(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    profile_organizer = tournament.profile_organizer
    return render(request, 'tournament_detail.html', {'tournament': tournament, 'profile_organizer': profile_organizer})


def viewParticipants(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    
    # Получаем все категории турнира
    categories = tournament.tournament_categories.all().select_related('template')
    
    # Создаем структуру данных для хранения участников
    participants_data = defaultdict(lambda: defaultdict(list))
    
    # Получаем всех зарегистрированных участников
    registrations = Registration.objects.filter(
        tournament=tournament
    ).select_related(
        'tournament_category',
        'profile_user',
        'profile_user__user',
        'unregistered_participant'
    ).prefetch_related(
        'payments'
    ).order_by(
        'tournament_category__template__name',
        'weight_category'
    )
    
    # Группируем участников по категориям и весам
    for reg in registrations:
        # Получаем последний платеж для регистрации
        last_payment = reg.payments.order_by('-created_at').first()
        payment_status = last_payment.status if last_payment else 'Не оплачено'
        
        if reg.profile_user:
            participant = {
                'name': reg.profile_user.get_full_name(),
                'email': reg.profile_user.user.email,
                'type': 'registered',
                'payment_status': payment_status,
                'payment_date': last_payment.created_at if last_payment else None
            }
        else:
            participant = {
                'name': f"{reg.unregistered_participant.last_name} {reg.unregistered_participant.first_name} {reg.unregistered_participant.surname}",
                'email': reg.unregistered_participant.email,
                'type': 'unregistered',
                'payment_status': payment_status,
                'payment_date': last_payment.created_at if last_payment else None
            }
        
        participants_data[reg.tournament_category][reg.weight_category].append(participant)
    
    # Создаем финальную структуру для шаблона
    categories_list = []
    for category in categories:
        weight_categories = []
        
        # Для стандартных весовых категорий из шаблона
        for weight in sorted(category.weight_categories):
            participants = participants_data[category].get(weight, [])
            if participants:  # Добавляем только если есть участники
                paid_count = sum(1 for p in participants if p['payment_status'] == 'succeeded')
                weight_categories.append({
                    'weight': weight,
                    'participants': participants,
                    'count': len(participants),
                    'paid_count': paid_count
                })
        
        # Для нестандартных весовых категорий (если есть)
        custom_weights = set(participants_data[category].keys()) - set(category.weight_categories)
        for weight in sorted(custom_weights):
            participants = participants_data[category][weight]
            if participants:  # Добавляем только если есть участники
                paid_count = sum(1 for p in participants if p['payment_status'] == 'succeeded')
                weight_categories.append({
                    'weight': weight,
                    'participants': participants,
                    'count': len(participants),
                    'paid_count': paid_count,
                    'custom': True
                })
        
        # Добавляем категорию только если в ней есть участники
        if weight_categories:
            total_paid = sum(w['paid_count'] for w in weight_categories)
            categories_list.append({
                'category': category,
                'weight_categories': weight_categories,
                'total_participants': sum(len(p) for p in participants_data[category].values()),
                'total_paid': total_paid
            })
    
    # Сортируем категории по имени
    categories_list.sort(key=lambda x: x['category'].template.name)
    
    return render(request, 'view_participants.html', {
        'tournament': tournament,
        'categories_list': categories_list
    })




def registrationTournament(request, pk):
    tournament = get_object_or_404(Tournament, pk=pk)
    
    # Проверка доступности регистрации
    if not tournament.is_registration_open():
        messages.error(request, "Регистрация на этот турнир закрыта")
        return redirect('tournaments:tournament_detail', pk=pk)

    # Проверка существующей регистрации
    existing_reg = None
    if request.user.is_authenticated and hasattr(request.user, 'profile_user'):
        existing_reg = Registration.objects.filter(
            tournament=tournament,
            profile_user=request.user.profile_user
        ).all()

    # Инициализируем формы
    reg_form = TournamentRegistrationForm(tournament=tournament, user=request.user)
    participant_form = None if request.user.is_authenticated and hasattr(request.user, 'profile_user') else UnregisteredParticipantForm()

    if request.method == 'POST':
        if request.user.is_authenticated and hasattr(request.user, 'profile_user'):
            # Авторизованный пользователь
            reg_form = TournamentRegistrationForm(request.POST, tournament=tournament, user=request.user)
            if reg_form.is_valid():
                try:
                    registration = reg_form.save(commit=False)
                    registration.profile_user = request.user.profile_user
                    registration.tournament = tournament
                    registration.save()
                    messages.success(request, "Вы успешно зарегистрированы на турнир!")
                    # Перенаправляем на страницу оплаты
                    return redirect('payments:create_payment', registration_id=registration.id)
                except Exception as e:
                    messages.error(request, f"Произошла ошибка при регистрации: {str(e)}")
            else:
                # Отображаем ошибки валидации
                for field, errors in reg_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{error}")
        else:
            # Неавторизованный пользователь
            participant_form = UnregisteredParticipantForm(request.POST)
            reg_form = TournamentRegistrationForm(request.POST, tournament=tournament, user=request.user)
            
            if participant_form.is_valid() and reg_form.is_valid():
                try:
                    # Сначала сохраняем данные неавторизованного участника
                    participant = participant_form.save()
                    
                    # Затем создаем регистрацию
                    registration = reg_form.save(commit=False)
                    registration.unregistered_participant = participant
                    registration.tournament = tournament
                    registration.save()
                    
                    messages.success(request, "Регистрация завершена успешно!")
                    # Перенаправляем на страницу оплаты
                    return redirect('payments:create_payment', registration_id=registration.id)
                except Exception as e:
                    messages.error(request, f"Произошла ошибка при регистрации: {str(e)}")
            else:
                # Отображаем ошибки валидации
                if not participant_form.is_valid():
                    for field, errors in participant_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Данные участника: {error}")
                
                if not reg_form.is_valid():
                    for field, errors in reg_form.errors.items():
                        for error in errors:
                            messages.error(request, f"Данные регистрации: {error}")

    return render(request, 'registration_tournament.html', {
        'tournament': tournament,
        'reg_form': reg_form,
        'participant_form': participant_form,
        'existing_reg': existing_reg,
        'user': request.user
    })

def get_category_info(request, category_id):
    """Получение информации о категории (веса, пояса и возрастные ограничения)"""
    category = get_object_or_404(TournamentCategory, pk=category_id)
    return JsonResponse({
        'weights': category.weight_categories,
        'belts': category.belt_levels,
        'age_from': category.template.age_from,
        'age_to': category.template.age_to
    })

def viewAllParticipants(request):
    # Получаем все регистрации с предзагрузкой связанных данных
    registrations = Registration.objects.all().select_related(
        'tournament',
        'tournament_category',
        'tournament_category__template',
        'profile_user',
        'unregistered_participant'
    ).prefetch_related(
        'payments'
    ).order_by(
        'tournament__tournament_start',
        'tournament_category__template__name',
        'weight_category'
    )
    
    # Группируем регистрации по турнирам
    tournaments_data = defaultdict(list)
    for reg in registrations:
        # Получаем последний платеж для регистрации
        last_payment = reg.payments.order_by('-created_at').first()
        payment_status = last_payment.status if last_payment else 'Не оплачено'
        
        # Формируем данные участника
        participant_data = {
            'registration': reg,
            'name': reg.profile_user.get_full_name() if reg.profile_user else 
                   f"{reg.unregistered_participant.last_name} {reg.unregistered_participant.first_name} {reg.unregistered_participant.surname}",
            'email': reg.profile_user.user.email if reg.profile_user else reg.unregistered_participant.email,
            'category': reg.tournament_category.actual_name,
            'weight': reg.weight_category,
            'belt': reg.belt_level,
            'payment_status': payment_status,
            'payment_date': last_payment.created_at if last_payment else None,
            'is_registered': bool(reg.profile_user)
        }
        
        tournaments_data[reg.tournament].append(participant_data)
    
    # Преобразуем в список для шаблона
    tournaments_list = [
        {
            'tournament': tournament,
            'participants': sorted(participants, key=lambda x: (x['category'], x['weight'])),
            'total_participants': len(participants),
            'paid_participants': sum(1 for p in participants if p['payment_status'] == 'succeeded')
        }
        for tournament, participants in tournaments_data.items()
    ]
    
    # Сортируем турниры по дате начала
    tournaments_list.sort(key=lambda x: x['tournament'].tournament_start)
    
    return render(request, 'view_all_participants.html', {
        'tournaments_list': tournaments_list
    })