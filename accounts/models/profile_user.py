from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class Profile_user(models.Model):
    # Поля для обычных пользователей
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True, null=True)
    first_name = models.CharField('Имя', max_length=100, blank=True, null=True)
    last_name = models.CharField('Фамилия', max_length=100, blank=True, null=True)
    surname = models.CharField('Отчество', max_length=100, blank=True, null=True)
    phone = models.CharField('Телефон', max_length=20, blank=True, null=True)
    birth_date = models.DateField('Дата рождения', null=True, blank=True)
    gender = models.CharField('Пол', max_length=1, choices=[('М', 'М'), ('Ж', 'Ж')], blank=True, null=True)
    clubs = models.ManyToManyField(
        'Club',
        related_name='members',
        blank=True,
        verbose_name=_('Клубы')
    )
    
    def __str__(self):
        return f'Профиль {self.user.username}'
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.surname}"