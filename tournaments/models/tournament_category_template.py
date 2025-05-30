from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext as _
from .fighting_style import FightingStyle

class TournamentCategoryTemplate(models.Model):
    """Шаблон стандартных категорий"""
    fighting_style = models.ForeignKey(FightingStyle, on_delete=models.CASCADE)
    category_type = models.CharField(max_length=20)  
    code = models.CharField(max_length=10) 
    name = models.CharField(max_length=40) 
    gender = models.CharField(max_length=1, choices=[('М', 'Мужчины'), ('Ж', 'Женщины')])
    age_from = models.PositiveSmallIntegerField(null=True, blank=True)
    age_to = models.PositiveSmallIntegerField(null=True, blank=True)
    weight_categories = ArrayField(models.PositiveSmallIntegerField(), default=list)
    is_standard = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Шаблон Категории')
        verbose_name_plural = _('Шаблоны Категорий')

    def no_weight(self):
        return f"{self.fighting_style} | {self.category_type} | {self.name} | {self.code} |"

    def __str__(self):
        return f"{self.category_type} | {self.name} | {self.code} | {self.weight_categories}" 