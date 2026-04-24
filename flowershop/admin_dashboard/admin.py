from django.contrib import admin

from .models import AdminActivityLog, AdminSetting, LoginAttempt


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ('username', 'status', 'ip_address', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('username', 'ip_address')


@admin.register(AdminActivityLog)
class AdminActivityLogAdmin(admin.ModelAdmin):
    list_display = ('admin_user', 'category', 'action', 'target_label', 'created_at')
    list_filter = ('category', 'created_at')
    search_fields = ('action', 'target_label', 'description')


@admin.register(AdminSetting)
class AdminSettingAdmin(admin.ModelAdmin):
    list_display = ('site_title', 'tax_rate', 'low_stock_threshold', 'session_timeout_minutes', 'updated_at')
