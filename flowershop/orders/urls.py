from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.create_order, name='create_order'),
    path('<int:order_id>/confirmation/', views.order_confirmation, name='order_confirmation'),
    path('track/', views.track_order, name='track_order'),
    path('<int:order_id>/detail/', views.order_detail, name='order_detail'),
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel_order'),
    path('my-orders/', views.my_orders, name='my_orders'),
]
