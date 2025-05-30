from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('registration/<int:registration_id>/payment/', views.create_payment, name='create_payment'),
    path('success/', views.payment_success, name='payment_success'),
    path('cancel/', views.payment_cancel, name='payment_cancel'),
] 