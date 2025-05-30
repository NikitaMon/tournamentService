from django.contrib import admin
from .models import TournamentCategoryTemplate, TournamentCategory, Tournament, FightingStyle, Registration

@admin.register(TournamentCategoryTemplate)
class TournamentCategoryTemplateAdmin(admin.ModelAdmin):
    list_display = ('fighting_style', 'category_type', 'code', 'name','gender', 'age_from', 'age_to', 'weight_categories', 'is_standard')
    list_filter = ('fighting_style', 'category_type', 'code', 'gender', 'is_standard')
    search_fields = ('fighting_style__name', 'category_type')
    

@admin.register(TournamentCategory)
class TournamentCategoryAdmin(admin.ModelAdmin):
    list_display = ('template', 'weight_categories', 'edit')
    list_filter = ('edit',)
    search_fields = ('template',)

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'registration_deadline')
    filter_horizontal = ('fighting_styles', 'tournament_categories')
    

@admin.register(FightingStyle)
class FightingStyleAdmin(admin.ModelAdmin):
    search_fields = ('name',)

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id', 'tournament', 'get_participant_name', 'tournament_category', 'weight_category', 'belt_level', 'get_payment_status')
    list_filter = ('tournament', 'tournament_category')
    search_fields = (
        'tournament__title',
        'profile_user__user__email',
        'profile_user__user__first_name',
        'profile_user__user__last_name',
        'unregistered_participant__email',
        'unregistered_participant__first_name',
        'unregistered_participant__last_name'
    )
    
    def get_participant_name(self, obj):
        if obj.profile_user:
            return f"{obj.profile_user.get_full_name()} (Зарегистрированный)"
        else:
            return f"{obj.unregistered_participant.last_name} {obj.unregistered_participant.first_name} {obj.unregistered_participant.surname} (Гость)"
    get_participant_name.short_description = 'Участник'
    
    def get_payment_status(self, obj):
        last_payment = obj.payments.order_by('-created_at').first()
        if last_payment:
            if last_payment.status == 'succeeded':
                return 'Оплачено'
            elif last_payment.status == 'pending':
                return 'В обработке'
            elif last_payment.status == 'canceled':
                return 'Отменено'
        return 'Не оплачено'
    get_payment_status.short_description = 'Статус оплаты'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('tournament', 'tournament_category', 'weight_category', 'belt_level')
        }),
        ('Информация об участнике', {
            'fields': ('profile_user', 'unregistered_participant')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Запрещаем создание регистраций через админку
    
    def has_change_permission(self, request, obj=None):
        return False  # Запрещаем изменение регистраций через админку