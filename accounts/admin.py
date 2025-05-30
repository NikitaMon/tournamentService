from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from accounts.models.club import Club
from accounts.models.coach import Coach
from .models import Profile_user, Profile_organizer


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'get_full_name', 'phone', 'clubs_count')
    search_fields = ('user__username', 'user__email', 'first_name', 'last_name', 'phone')
    list_select_related = ('user',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'
    get_username.admin_order_field = 'user__username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    get_full_name.short_description = 'ФИО'
    
    def clubs_count(self, obj):
        return obj.clubs.count()
    clubs_count.short_description = 'Количество клубов'
    
    fieldsets = (
        ('Данные пользователя', {
            'fields': ('user', 'user_first_name', 'user_last_name', 'user_email')
        }),
        ('Профиль тренера', {
            'fields': ('avatar', 'first_name', 'last_name', 'surname', 'phone', 
                      'birth_date', 'gender', 'experience', 'specialization', 'bio')
        }),
        ('Участники', {
            'fields': ('participants', 'unregistered_participants'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('user_first_name', 'user_last_name', 'user_email')
    
    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'
    
    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ('name', 'coach', 'location', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'location', 'description', 'coach__user__username', 'coach__user__email')
    list_select_related = ('coach', 'coach__user')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'coach', 'location')
        }),
        ('Дополнительная информация', {
            'fields': ('description',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Profile_user)
class ProfileUserAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'phone', 'birth_date')
    list_select_related = ('user',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'
    get_username.admin_order_field = 'user__username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    # Форма редактирования с полями из User
    fieldsets = (
        ('Данные пользователя', {
            'fields': ('user', 'user_first_name', 'user_last_name', 'user_email')
        }),
        ('Профиль', {
            'fields': ('avatar', 'surname', 'phone', 'birth_date', 'gender')
        }),
    )
    
    readonly_fields = ('user_first_name', 'user_last_name', 'user_email')
    
    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'
    
    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


@admin.register(Profile_organizer)
class Profile_organizerAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'company_phone', 'company_name')
    list_select_related = ('user',)
    
    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = 'Логин'
    get_username.admin_order_field = 'user__username'
    
    def get_email(self, obj):
        return obj.user.email
    get_email.short_description = 'Email'
    get_email.admin_order_field = 'user__email'
    
    # Форма редактирования с полями из User
    fieldsets = (
        ('Данные пользователя', {
            'fields': ('user', 'user_first_name', 'user_last_name', 'user_email')
        }),
        ('Профиль', {
            'fields': ('surname', 'avatar', 'tax_id', 'company_phone', 'company_name', 'company_address', 'change_avaliable')
        }),
    )
    
    readonly_fields = ('user_first_name', 'user_last_name', 'user_email')
    
    def user_first_name(self, obj):
        return obj.user.first_name
    user_first_name.short_description = 'Имя'
    
    def user_last_name(self, obj):
        return obj.user.last_name
    user_last_name.short_description = 'Фамилия'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'Email'


