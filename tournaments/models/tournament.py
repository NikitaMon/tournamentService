from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator
from .fighting_style import FightingStyle

class Tournament(models.Model):
    """Модель турнира"""
    fighting_styles = models.ManyToManyField(
        FightingStyle, 
        blank=True
    )
    profile_organizer = models.ForeignKey(
        'accounts.Profile_organizer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    title = models.CharField(
        _('Название турнира'),
        max_length=200,
        unique=True
    )
    image = models.ImageField(
        _('Изображение'),
        upload_to='tournaments/',
        blank=True
    )
    location = models.TextField(
        _('Место проведения')
    )
    description = models.TextField(
        _('Описание'),
        blank=True
    )
    # Периоды регистрации
    early_registration_start = models.DateTimeField(
        _('Начало ранней регистрации'), 
        null=True, blank=True
    )
    early_registration_price = models.DecimalField(
        _('Цена ранней регистрации'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)], 
        null=True, blank=True
    )
    regular_registration_start = models.DateTimeField(
        _('Начало обычной регистрации'), 
        null=True
    )
    regular_registration_price = models.DecimalField(
        _('Цена обычной регистрации'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)], 
        null=True,
    )
    late_registration_start = models.DateTimeField(
        _('Начало поздней регистрации'), 
        null=True, blank=True
    )
    late_registration_price = models.DecimalField(
        _('Цена поздней регистрации'),
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)], 
        null=True, blank=True
    )
    registration_deadline = models.DateTimeField(
        _('Дата завершения регистрации')
    )
    
    tournament_start = models.DateTimeField(
        _('Дата начала соревнований'), 
    )
    
    tournament_end = models.DateTimeField(
        _('Дата окончания соревнований'), 
    )
    # Связь многие-ко-многим с видами борьбы
    tournament_categories = models.ManyToManyField(
        'TournamentCategory',
        verbose_name=_('Категории'),
        related_name='tournaments',
        blank=True,
    )
    
    # Автоматические метки времени
    created_at = models.DateTimeField(
        _('Дата создания'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('Дата обновления'),
        auto_now=True
    )

    max_participants = models.PositiveIntegerField(
        _('Максимальное количество участников'),
        null=True,
        blank=True
    )
    payment_required = models.BooleanField(
        _('Требуется оплата'),
        default=True
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Черновик'),
            ('published', 'Опубликован'),
            ('cancelled', 'Отменен')
        ],
        default='draft'
    )
    newbies = models.BooleanField(
        _('Участие новичков'),
        default=False
    )

    class Meta:
        verbose_name = _('Турнир')
        verbose_name_plural = _('Турниры')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['registration_deadline']),
        ]

    def __str__(self):
        return self.title

    def get_current_participants_count(self):
        """Возвращает текущее количество участников"""
        return self.registrations.count()

    def is_registration_open(self):
        """Проверяет, открыта ли регистрация"""
        from django.utils import timezone
        now = timezone.now()
        
        # Если нет ранней и поздней регистрации
        if self.early_registration_start is None and self.late_registration_start is None:
            if self.regular_registration_start and now >= self.regular_registration_start and now <= self.registration_deadline:
                return True
            return False

        # Проверяем периоды регистрации
        if self.early_registration_start and now >= self.early_registration_start:
            if self.regular_registration_start and now < self.regular_registration_start:
                return True
            elif self.regular_registration_start and now >= self.regular_registration_start:
                if self.late_registration_start and now < self.late_registration_start:
                    return True
                elif self.late_registration_start and now >= self.late_registration_start:
                    return now <= self.registration_deadline
                return now <= self.registration_deadline
        return False

    def get_status(self):
        """Возвращает текущий статус турнира"""
        from django.utils import timezone
        now = timezone.now()

        if now < self.registration_deadline:
            return 'registration_open'
        elif now < self.tournament_start:
            return 'registration_closed'
        elif now < self.tournament_end:
            return 'in_progress'
        else:
            return 'completed'

    def get_current_registration_price(self):
        """Возвращает текущую цену регистрации на основе дат"""
        from django.utils import timezone
        now = timezone.now()
        
        # Если нет ранней и поздней регистрации
        if self.early_registration_start is None and self.late_registration_start is None:
            if self.regular_registration_start and now >= self.regular_registration_start and now <= self.registration_deadline:
                return self.regular_registration_price
            return None

        # Проверяем периоды регистрации
        if self.early_registration_start and now >= self.early_registration_start:
            if self.regular_registration_start and now < self.regular_registration_start:
                return self.early_registration_price
            elif self.regular_registration_start and now >= self.regular_registration_start:
                if self.late_registration_start and now < self.late_registration_start:
                    return self.regular_registration_price
                elif self.late_registration_start and now >= self.late_registration_start:
                    if now <= self.registration_deadline:
                        return self.late_registration_price
                    return None
                elif now <= self.registration_deadline:
                    return self.regular_registration_price
                return None
        return None

    def get_current_registration_info(self):
        """Возвращает текст с типом и датой текущей регистрации"""
        from django.utils import timezone
        now = timezone.now()

        # Если нет ранней и поздней регистрации
        if self.early_registration_start is None and self.late_registration_start is None:
            if self.regular_registration_start and now >= self.regular_registration_start and now <= self.registration_deadline:
                return _("Регистрация открыта до {}").format(
                    self.registration_deadline.strftime("%d.%m.%Y")
                )
            return _("Регистрация закрыта")

        # Проверяем периоды регистрации
        if self.early_registration_start and now >= self.early_registration_start:
            if self.regular_registration_start and now < self.regular_registration_start:
                return _("Ранняя регистрация открыта до {}").format(
                    self.regular_registration_start.strftime("%d.%m.%Y")
                )
            elif self.regular_registration_start and now >= self.regular_registration_start:
                if self.late_registration_start and now < self.late_registration_start:
                    return _("Обычная регистрация открыта до {}").format(
                        self.late_registration_start.strftime("%d.%m.%Y")
                    )
                elif self.late_registration_start and now >= self.late_registration_start:
                    if now <= self.registration_deadline:
                        return _("Поздняя регистрация открыта до {}").format(
                            self.registration_deadline.strftime("%d.%m.%Y")
                        )
                    return _("Регистрация закрыта")
                elif now <= self.registration_deadline:
                    return _("Обычная регистрация открыта до {}").format(
                        self.registration_deadline.strftime("%d.%m.%Y")
                    )
                return _("Регистрация закрыта")
        return _("Регистрация еще не началась")
        
    def get_org_profile(self):
        return self.profile_organizer
    
    def deadline(self):
        return self.registration_deadline
    
    def fs_qset(self):
        data = self.fighting_styles.all().values_list()
        return "\n".join(str(x[1]) for x in data)
    
    def category_t(self):
        return self.tournament_categories 