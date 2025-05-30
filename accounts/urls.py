from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('registration/', views.registration, name='registration'),
    # path('registration/organizer', views.registration_organizer, name='registration_organizer'),
    
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    path('profile/', views.profile_view, name='profile'),
    path('profile/create-club/', views.create_club, name='create_club'),
    path('profile/edit-club/<int:club_id>/', views.edit_club, name='edit_club'),
    path('profile/delete-club/<int:club_id>/', views.delete_club, name='delete_club'),
    path('coach/<int:coach_id>/clubs/', views.get_coach_clubs, name='get_coach_clubs'),
    
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/join-club/', views.join_club, name='join_club'),
    path('profile/leave-club/<int:club_id>/', views.leave_club, name='leave_club'),
    path('profile/remove-member/<int:club_id>/<int:member_id>/', views.remove_member, name='remove_member'),
    
    path('profile/delete-avatar/', views.delete_avatar_view, name='delete_avatar'),
    path('profile/save-avatar/', views.save_avatar_view, name='save_avatar'),
    path('profile/change_avatar/', views.change_avatar, name='change_avatar'),
]