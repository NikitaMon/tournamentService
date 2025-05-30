from django.db import models
from django.contrib.auth.models import User

class Profile_organizer(models.Model):
    # Поля для Организаторов
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField('Аватар', upload_to='avatars/', blank=True)
    first_name = models.CharField('Имя', max_length=100, blank=True)
    last_name = models.CharField('Фамилия', max_length=100, blank=True)
    surname = models.CharField('Отчество', max_length=100, blank=True)
    company_name = models.CharField('Название компании', max_length=100, blank=True)
    company_address = models.TextField('Адрес компании', blank=True)
    company_phone = models.CharField('Телефон', max_length=20, blank=True)
    tax_id = models.CharField('ИНН', max_length=20, blank=True)
    balance = models.DecimalField('Баланс', max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f'Профиль {self.user.username}'
    
    def get_full_name(self):
        return f"{self.last_name} {self.first_name} {self.surname}"