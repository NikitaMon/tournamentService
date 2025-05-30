from django.shortcuts import render, get_object_or_404
#from .forms import RegisterForm, UserUpdateForm, ProfileUserForm, ProfileOrganizerForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from accounts.forms import RegisterForm, CoachProfileForm, OrganizerProfileForm
from django.contrib.auth.models import Group
from accounts.models import Club, Coach
import logging
from django.http import JsonResponse
from accounts.models.profile_user import Profile_user

logger = logging.getLogger(__name__)

def registration(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            logger.info(f"Form is valid. User type: {form.cleaned_data.get('user_type')}")
            user = form.save()
            logger.info(f"User created: {user.username}")
            login(request, user)  # Автоматический вход после регистрации
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('accounts:profile')
        else:
            logger.error(f"Form errors: {form.errors}")
    else:
        form = RegisterForm()

    context: dict = {
        'title': 'Регистрация пользователя',
    }
    
    return render(request, 'registration/registration.html', {'form': form, 'context': context})

# @login_required
# def registration_organizer(request):
#     if request.method == 'POST':
#         form = RegisterForm(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             user._profile_type = 'organizer' 
#             user.save()  
#             return redirect('/')
#     else:
#         form = RegisterForm()
#         context: dict = {
#             'title': 'Регистрация организатора',
#         }

#     return render(request, 'registration/registration.html', {'form': form, 'context': context})


@login_required
def profile_view(request):
    if hasattr(request.user, 'coach'):
        profile = request.user.coach
        coach = profile
        clubs = Club.objects.filter(coach=profile).order_by('-created_at')
        available_clubs = None
    elif hasattr(request.user, 'profile_user'):
        profile = request.user.profile_user
        coach = None
        clubs = None
        # Получаем список доступных клубов (кроме тех, в которых уже состоит пользователь)
        available_clubs = Club.objects.exclude(
            id__in=profile.clubs.values_list('id', flat=True)
        ).order_by('name')
    elif hasattr(request.user, 'profile_organizer'):
        profile = request.user.profile_organizer
        coach = None
        clubs = None
        available_clubs = None
    else:
        profile = None
        coach = None
        clubs = None
        available_clubs = None

    context = {
        'profile': profile,
        'coach': coach,
        'clubs': clubs,
        'available_clubs': available_clubs,
        'title': 'Профиль пользователя'
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit_view(request):
    try:
        # Получаем тип профиля через getattr с дефолтным значением None
        profile_type = next(
            (attr for attr in ['profile_user', 'profile_organizer', 'coach'] 
             if hasattr(request.user, attr)),
            None
        )
        
        if profile_type is None:
            messages.error(request, 'Профиль не найден')
            return redirect('accounts:profile')
            
        # Вызываем соответствующую функцию редактирования
        edit_functions = {
            'profile_user': edit_profile_user,
            'profile_organizer': edit_organizer_profile,
            'coach': edit_coach_profile
        }
        
        return edit_functions[profile_type](request)
        
    except Exception as e:
        logger.error(f"Error in profile_edit_view: {str(e)}")
        messages.error(request, 'Произошла ошибка при редактировании профиля')
        return redirect('accounts:profile')
    



@login_required
def delete_avatar_view(request):
    if request.method == 'POST':
        try:
            if hasattr(request.user, 'profile_user'):
                profile = request.user.profile_user
            elif hasattr(request.user, 'profile_organizer'):
                profile = request.user.profile_organizer
            elif hasattr(request.user, 'coach'):
                profile = request.user.coach
            else:
                messages.error(request, 'Профиль не найден')
                return redirect('accounts:change_avatar')
                
            if profile.avatar:
                profile.avatar.delete()
                profile.avatar = None 
                profile.save()           
                messages.success(request, 'Аватар успешно удален')
            else:
                messages.info(request, 'Аватар отсутствует')
        except Exception as e:
            logger.error(f"Error deleting avatar: {str(e)}")
            messages.error(request, f'Ошибка при удалении аватара: {str(e)}')
            
    return redirect('accounts:change_avatar')

@login_required
def save_avatar_view(request):
    if request.method == 'POST':
        try:
            if not request.FILES.get('avatar'):
                messages.error(request, 'Файл не выбран')
                return redirect('accounts:change_avatar')
                
            if hasattr(request.user, 'profile_user'):
                profile = request.user.profile_user
            elif hasattr(request.user, 'profile_organizer'):
                profile = request.user.profile_organizer
            elif hasattr(request.user, 'coach'):
                profile = request.user.coach
            else:
                messages.error(request, 'Профиль не найден')
                return redirect('accounts:change_avatar')
                
            avatar = request.FILES['avatar']
            
            # Проверяем тип файла
            if not avatar.content_type.startswith('image/'):
                messages.error(request, 'Пожалуйста, загрузите изображение')
                return redirect('accounts:change_avatar')
                
            # Проверяем размер файла (максимум 5MB)
            if avatar.size > 5 * 1024 * 1024:
                messages.error(request, 'Размер файла не должен превышать 5MB')
                return redirect('accounts:change_avatar')
                
            # Удаляем старый аватар если он существует
            if profile.avatar:
                profile.avatar.delete()
                
            profile.avatar = avatar
            profile.save()
            messages.success(request, 'Аватар успешно сохранен!')
        except Exception as e:
            logger.error(f"Error saving avatar: {str(e)}")
            messages.error(request, f'Ошибка при сохранении аватара: {str(e)}')
            
    return redirect('accounts:profile')

@login_required
def change_avatar(request):
    try:
        if hasattr(request.user, 'profile_user'):
            profile = request.user.profile_user
        elif hasattr(request.user, 'profile_organizer'):
            profile = request.user.profile_organizer
        elif hasattr(request.user, 'coach'):
            profile = request.user.coach
        else:
            messages.error(request, 'Профиль не найден')
            return redirect('accounts:profile')
            
        context = {
            'title': 'Редактирование аватара',
            'profile': profile,
        }
        return render(request, 'accounts/change_avatar.html', context)
    except Exception as e:
        logger.error(f"Error in change_avatar view: {str(e)}")
        messages.error(request, 'Произошла ошибка при загрузке страницы')
        return redirect('accounts:profile')

@login_required
def create_club(request):
    if request.method == 'POST':
        try:
            # Создаем новый клуб
            club = Club.objects.create(
                name=request.POST.get('name'),
                location=request.POST.get('location'),
                description=request.POST.get('description', ''),
                coach=request.user.coach
            )
            
            messages.success(request, 'Клуб успешно создан!')
        except Exception as e:
            logger.error(f"Error creating club: {str(e)}")
            messages.error(request, 'Произошла ошибка при создании клуба')
            
    return redirect('accounts:profile')

@login_required
def edit_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Проверяем, является ли текущий пользователь тренером этого клуба
    if not hasattr(request.user, 'coach') or request.user.coach != club.coach:
        messages.error(request, 'У вас нет прав для редактирования этого клуба')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        try:
            club.name = request.POST.get('name')
            club.location = request.POST.get('location')
            club.description = request.POST.get('description', '')
            club.save()
            messages.success(request, 'Клуб успешно обновлен!')
        except Exception as e:
            logger.error(f"Error updating club: {str(e)}")
            messages.error(request, 'Произошла ошибка при обновлении клуба')
            
    return redirect('accounts:profile')

@login_required
def delete_club(request, club_id):
    club = get_object_or_404(Club, id=club_id)
    
    # Проверяем, является ли текущий пользователь тренером этого клуба
    if not hasattr(request.user, 'coach') or request.user.coach != club.coach:
        messages.error(request, 'У вас нет прав для удаления этого клуба')
        return redirect('accounts:profile')
    
    if request.method == 'POST':
        try:
            club.delete()
            messages.success(request, 'Клуб успешно удален!')
        except Exception as e:
            logger.error(f"Error deleting club: {str(e)}")
            messages.error(request, 'Произошла ошибка при удалении клуба')
            
    return redirect('accounts:profile')

@login_required
def get_coach_clubs(request, coach_id):
    """Получение списка клубов тренера по его ID"""
    try:
        coach = get_object_or_404(Coach, id=coach_id)
        clubs = Club.objects.filter(coach=coach).values('id', 'name', 'location', 'description', 'created_at', 'updated_at')
        
        # Преобразуем QuerySet в список словарей
        clubs_list = list(clubs)
        
        # Форматируем даты
        for club in clubs_list:
            club['created_at'] = club['created_at'].strftime('%d.%m.%Y')
            club['updated_at'] = club['updated_at'].strftime('%d.%m.%Y')
        
        return JsonResponse({
            'status': 'success',
            'coach_name': str(coach),
            'clubs': clubs_list
        })
    except Exception as e:
        logger.error(f"Error getting coach clubs: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Произошла ошибка при получении списка клубов'
        }, status=400)

@login_required
def edit_coach_profile(request):
    """Редактирование профиля тренера"""
    if not hasattr(request.user, 'coach'):
        messages.error(request, 'У вас нет прав для редактирования профиля тренера')
        return redirect('accounts:profile')
    
    coach = request.user.coach
    
    if request.method == 'POST':
        form = CoachProfileForm(request.POST, instance=coach)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CoachProfileForm(instance=coach)
    
    context = {
        'form': form,
        'title': 'Редактирование профиля',
        'profile': coach
    }
    return render(request, 'accounts/profile_edit.html', context)

@login_required
def edit_profile_user(request):
    """Редактирование профиля пользователя"""
    if not hasattr(request.user, 'profile_user'):
        messages.error(request, 'У вас нет прав для редактирования профиля пользователя')
        return redirect('accounts:profile')
    
    profile_user = request.user.profile_user
    
    if request.method == 'POST':
        form = CoachProfileForm(request.POST, instance=profile_user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = CoachProfileForm(instance=profile_user)
    
    context = {
        'form': form,
        'title': 'Редактирование профиля',
        'profile': profile_user
    }
    return render(request, 'accounts/profile_edit.html', context)
    





@login_required
def join_club(request):
    """Присоединение пользователя к клубу"""
    if request.method == 'POST':
        try:
            club_id = request.POST.get('club_id')
            club = get_object_or_404(Club, id=club_id)
            
            # Проверяем, не состоит ли уже пользователь в этом клубе
            if club in request.user.profile_user.clubs.all():
                messages.warning(request, 'Вы уже состоите в этом клубе')
            else:
                request.user.profile_user.clubs.add(club)
                messages.success(request, f'Вы успешно присоединились к клубу "{club.name}"')
                
        except Exception as e:
            logger.error(f"Error joining club: {str(e)}")
            messages.error(request, 'Произошла ошибка при присоединении к клубу')
            
    return redirect('accounts:profile')

@login_required
def leave_club(request, club_id):
    """Выход пользователя из клуба"""
    if request.method == 'POST':
        try:
            club = get_object_or_404(Club, id=club_id)
            
            # Проверяем, состоит ли пользователь в этом клубе
            if club in request.user.profile_user.clubs.all():
                request.user.profile_user.clubs.remove(club)
                messages.success(request, f'Вы успешно покинули клуб "{club.name}"')
            else:
                messages.warning(request, 'Вы не состоите в этом клубе')
                
        except Exception as e:
            logger.error(f"Error leaving club: {str(e)}")
            messages.error(request, 'Произошла ошибка при выходе из клуба')
            
    return redirect('accounts:profile')

@login_required
def remove_member(request, club_id, member_id):
    """Исключение участника из клуба"""
    if request.method == 'POST':
        try:
            club = get_object_or_404(Club, id=club_id)
            member = get_object_or_404(Profile_user, id=member_id)
            
            # Проверяем, является ли текущий пользователь тренером этого клуба
            if not hasattr(request.user, 'coach') or request.user.coach != club.coach:
                messages.error(request, 'У вас нет прав для исключения участников из этого клуба')
                return redirect('accounts:profile')
            
            # Проверяем, состоит ли участник в этом клубе
            if member in club.members.all():
                member_name = member.get_full_name() or member.user.username
                club.members.remove(member)
                messages.success(request, f'Участник {member_name} успешно исключен из клуба')
            else:
                messages.warning(request, 'Этот участник не состоит в клубе')
                
        except Exception as e:
            logger.error(f"Error removing member from club: {str(e)}")
            messages.error(request, 'Произошла ошибка при исключении участника из клуба')
            
    return redirect('accounts:profile')

@login_required
def edit_organizer_profile(request):
    """Редактирование профиля организатора"""
    if not hasattr(request.user, 'profile_organizer'):
        messages.error(request, 'У вас нет прав для редактирования профиля организатора')
        return redirect('accounts:profile')
    
    organizer = request.user.profile_organizer
    
    if request.method == 'POST':
        form = OrganizerProfileForm(request.POST, request.FILES, instance=organizer)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        form = OrganizerProfileForm(instance=organizer)
    
    context = {
        'form': form,
        'title': 'Редактирование профиля',
        'profile': organizer
    }
    return render(request, 'accounts/profile_edit.html', context)