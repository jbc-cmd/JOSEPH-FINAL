from django.urls import path
from . import views

app_name = 'custom_bouquet'

urlpatterns = [
    path('builder/', views.bouquet_builder, name='builder'),
    path('pricing/', views.get_bouquet_pricing, name='pricing'),
    path('save/', views.save_custom_bouquet, name='save'),
    path('flower/<int:flower_id>/', views.get_flower_details, name='flower_details'),
]
