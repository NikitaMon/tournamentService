from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import gettext as _
from .tournament_category_template import TournamentCategoryTemplate

class TournamentCategory(models.Model):
    """Конкретные категории для турнира"""
    template = models.ForeignKey(
        TournamentCategoryTemplate,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    weight_categories = ArrayField(models.PositiveSmallIntegerField(), default=list, null=True, blank=True)
    belt_levels = ArrayField(models.CharField(max_length=50), default=list, null=True, blank=True)
    edit = models.BooleanField(default=False)

    class Meta:
        verbose_name = _('Категория')
        verbose_name_plural = _('Категории')

    def actual_weights(self):
        return f"edit: {self.weight_categories}" if self.edit else f"standard: {self.template.weight_categories}"
    
    def actual_name(self):
        return f"{self.template.name}"

    def ful_name(self):
        return f"{self.template.no_weight()} | {self.actual_weights()} "
    
    def __str__(self):
        return f"{self.template.name} [{self.template.fighting_style}]" 