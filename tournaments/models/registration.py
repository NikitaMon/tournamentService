from django.db import models
from django.utils.translation import gettext as _
from .tournament import Tournament
from .tournament_category import TournamentCategory

class Registration(models.Model):
    """Модель регистрации участника на турнир"""
    tournament = models.ForeignKey(
        Tournament,
        on_delete=models.CASCADE,
        related_name='registrations',
    )
    tournament_category = models.ForeignKey(
        TournamentCategory,
        on_delete=models.CASCADE,
        verbose_name=_('Категории'),
        related_name='registrations'
    )
    weight_category = models.PositiveSmallIntegerField('Весовая категория')
    belt_level = models.CharField(_('Уровень пояса'), max_length=50)
    unregistered_participant = models.ForeignKey(
        'accounts.UnregisteredParticipant',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='registrations'
    )
    profile_user = models.ForeignKey(
        'accounts.Profile_user',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='registrations'
    )
    newbies = models.BooleanField(
        _('Новичок'),
        default=False
    )
    registration_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = [
            ('tournament', 'profile_user', 'tournament_category'),
            ('tournament', 'unregistered_participant', 'tournament_category')
        ]
    
    def __str__(self):
        participant = self.profile_user or self.unregistered_participant
        return f"{participant} - {self.tournament.title} ({self.tournament_category.actual_name})" 