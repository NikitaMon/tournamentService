from django.db import models
from django.utils.translation import gettext as _


class UnregisteredParticipant(models.Model):
    """Участник без аккаунта в системе"""
    first_name = models.CharField('Имя', max_length=100)
    last_name = models.CharField('Фамилия', max_length=100)
    surname = models.CharField('Отчество', max_length=100)
    gender = models.CharField(max_length=1, choices=[('М', 'Мужчины'), ('Ж', 'Женщины')])
    birth_date = models.DateField('Дата рождения')
    phone = models.CharField('Телефон', max_length=20)
    email = models.EmailField('Email')
    created_at = models.DateTimeField(auto_now_add=True)
    clubs = models.ManyToManyField(
        'Club',
        related_name='unregistered_participants',
        blank=True,
        verbose_name=_('Клубы')
    )

    class Meta:
        verbose_name = 'Незарегистрированный участник'
        verbose_name_plural = 'Незарегистрированные участники'

    def __str__(self):
        return f"{self.last_name} {self.first_name} {self.surname}"
