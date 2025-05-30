from django.db import models
from django.utils.translation import gettext as _

class FightingStyle(models.Model):
    """Модель для видов борьбы"""
    name = models.CharField(
        _('Вид борьбы'),
        max_length=100,
        unique=True
    )

    class Meta:
        verbose_name = _('Вид борьбы')
        verbose_name_plural = _('Виды борьбы')
        ordering = ['name']

    def __str__(self):
        return self.name 