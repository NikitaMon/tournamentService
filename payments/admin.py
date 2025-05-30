from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'registration', 'amount', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    search_fields = ('registration__tournament__title', 'payment_id', 'registration__profile_user__user__email', 'registration__unregistered_participant__email')
    readonly_fields = ('payment_id', 'amount', 'status', 'payment_url', 'created_at', 'updated_at')
    ordering = ('-created_at',)
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('registration', 'payment_id', 'amount', 'status')
        }),
        ('Дополнительная информация', {
            'fields': ('payment_url', 'created_at', 'updated_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Запрещаем создание платежей через админку
    
    def has_change_permission(self, request, obj=None):
        return False  # Запрещаем изменение платежей через админку
