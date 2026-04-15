"""
URL configuration for flowershop_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from products import views as product_views
from .views import health_check

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('health/', health_check, name='health_check'),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('bouquet/', include('custom_bouquet.urls')),
    path('', product_views.HomeView.as_view(), name='home'),  # Home page
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Customize admin site
admin.site.site_header = "Joseph Flowershop Admin"
admin.site.site_title = "Admin"
admin.site.index_title = "Welcome to Joseph Flowershop Admin"
