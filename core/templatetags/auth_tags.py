from django import template


register = template.Library()

@register.filter(name='in_group')
def in_group(user, group_name):
    """
    Проверяет, принадлежит ли пользователь к указанной группе.
    Использование в шаблоне: {% if user|in_group:'group_name' %}
    """
    return user.groups.filter(name=group_name).exists()


@register.filter(name='has_profile')
def has_profile(user, profile_type):
    """
    Проверяет наличие определенного типа профиля у пользователя.
    Использование в шаблоне: {% if user|has_profile:'user' %}
    """
    if profile_type == 'user':
        return hasattr(user, 'profile_user')
    elif profile_type == 'organizer':
        return hasattr(user, 'profile_organizer')
    return False


@register.simple_tag
def get_user_profile(user):
    """
    Возвращает профиль пользователя в зависимости от его типа.
    Использование в шаблоне: {% get_user_profile user as profile %}
    """
    if hasattr(user, 'profile_user'):
        return user.profile_user
    elif hasattr(user, 'profile_organizer'):
        return user.profile_organizer
    return None 