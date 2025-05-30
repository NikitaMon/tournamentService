from django.db import models
from django.utils.translation import gettext_lazy as _
from .coach import Coach

class Club(models.Model):
    """Модель спортивного клуба"""
    name = models.CharField(max_length=100, verbose_name=_('Название клуба'))
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name='clubs', verbose_name=_('Тренер'))
    location = models.TextField(verbose_name=_('Место расположения'))
    description = models.TextField(blank=True, verbose_name=_('Описание'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Дата создания'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Дата обновления'))

    class Meta:
        verbose_name = _('Клуб')
        verbose_name_plural = _('Клубы')
        ordering = ['-created_at']

    def __str__(self):
        return self.name 