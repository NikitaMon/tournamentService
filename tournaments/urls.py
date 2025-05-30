from django.urls import path
from . import views

app_name = 'tournaments'

urlpatterns = [
    path('', views.index, name='index'),
    path('latest/', views.latest, name='latest'),
    path('myRegistrations/', views.myRegistrations, name='myRegistrations'),

    path('create/', views.createTournament, name='create_tournament'),
    path('get-weights-form/', views.get_weights_form, name='get_weights_form'),
    path('get-categories/', views.get_categories, name='get_categories'),
    
    path('<int:pk>/', views.tournament_detail, name='tournament_detail'),
    path('<int:pk>/registration_tournament/', views.registrationTournament, name='registration_tournament'),
    path('get-category-info/<int:category_id>/', views.get_category_info, name='get_category_info'),
    path('<int:pk>/viewParticipants/', views.viewParticipants, name='viewParticipants'),
    path('tournament/<int:pk>/participants/', views.viewParticipants, name='view_participants'),
    path('participants/', views.viewAllParticipants, name='view_all_participants'),
    # path('registration/<int:pk>/cancel/', views.cancelRegistration, name='cancel_registration'),
]