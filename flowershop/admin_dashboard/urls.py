from django.urls import path

from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('users/', views.user_list, name='users'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-status/', views.toggle_user_status, name='toggle_user_status'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/<int:user_id>/reset-password/', views.reset_user_password, name='reset_user_password'),
    path('security/', views.security_dashboard, name='security'),
    path('products/', views.product_list, name='products'),
    path('products/add/', views.product_create, name='product_add'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('categories/', views.category_list, name='categories'),
    path('categories/add/', views.category_create, name='category_add'),
    path('categories/<int:category_id>/edit/', views.category_edit, name='category_edit'),
    path('categories/<int:category_id>/delete/', views.category_delete, name='category_delete'),
    path('orders/', views.order_list, name='orders'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/status/', views.update_order_status, name='update_order_status'),
    path('orders/<int:order_id>/refund/<int:refund_id>/', views.update_refund_status, name='update_refund_status'),
    path('orders/export/csv/', views.export_orders_csv, name='export_orders_csv'),
    path('orders/export/pdf/', views.export_orders_pdf, name='export_orders_pdf'),
    path('reports/', views.report_list, name='reports'),
    path('reports/export/csv/', views.export_reports_csv, name='export_reports_csv'),
    path('reports/export/pdf/', views.export_reports_pdf, name='export_reports_pdf'),
    path('inventory/', views.inventory_dashboard, name='inventory'),
    path('notifications/', views.notification_center, name='notifications'),
    path('settings/', views.settings_dashboard, name='settings'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
]
