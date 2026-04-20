from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/information/', views.profile_information, name='profile_information'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('orders/', views.order_history, name='order_history'),
    path('address/add/', views.DeliveryAddressCreateView.as_view(), name='add_address'),
    path('address/<int:pk>/edit/', views.DeliveryAddressUpdateView.as_view(), name='edit_address'),
    path('address/<int:pk>/delete/', views.DeliveryAddressDeleteView.as_view(), name='delete_address'),
]
