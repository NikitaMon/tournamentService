from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class Coach(models.Model):
    """Модель тренера"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name=_('Пользователь'))
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    first_name = models.CharField('Имя', max_length=100, blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=100, blank=True, null=True)
    surname = models.CharField('Отчество', max_length=100, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    gender = models.CharField('Пол', max_length=1, choices=[('М', 'М'), ('Ж', 'Ж')], blank=True, null=True)
    participants = models.ManyToManyField(
        'Profile_user',
        related_name='coaches',
        blank=True,
        verbose_name=_('Участники')
    )
    unregistered_participants = models.ManyToManyField(
        'UnregisteredParticipant',
        related_name='coaches',
        blank=True,
        verbose_name=_('Незарегистрированные участники')
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Тренер')
        verbose_name_plural = _('Тренеры')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username}"

    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.surname}"
