from django.urls import path

from . import views

app_name = 'payments'

urlpatterns = [
    path('paymongo/webhook/', views.paymongo_webhook, name='paymongo_webhook'),
    path('paymongo/return/', views.paymongo_return, name='paymongo_return'),
]
