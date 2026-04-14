from django.contrib import admin
from .models import Payment, RefundRequest


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['order', 'payment_method', 'amount', 'status', 'created_at']
    list_filter = ['payment_method', 'status', 'created_at']
    search_fields = ['order__order_number', 'transaction_id', 'reference_number']
    readonly_fields = ['created_at', 'updated_at', 'paid_at']
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order',)
        }),
        ('Payment Details', {
            'fields': ('payment_method', 'amount', 'status')
        }),
        ('Transaction Information', {
            'fields': ('transaction_id', 'payment_gateway', 'reference_number'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_failed', 'mark_as_refunded']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        for payment in queryset:
            payment.status = 'COMPLETED'
            payment.paid_at = timezone.now()
            payment.save(update_fields=['status', 'paid_at', 'updated_at'])
    mark_as_completed.short_description = "Mark selected payments as Completed"
    
    def mark_as_failed(self, request, queryset):
        for payment in queryset:
            payment.status = 'FAILED'
            payment.save(update_fields=['status', 'updated_at'])
    mark_as_failed.short_description = "Mark selected payments as Failed"
    
    def mark_as_refunded(self, request, queryset):
        for payment in queryset:
            payment.status = 'REFUNDED'
            payment.save(update_fields=['status', 'updated_at'])
    mark_as_refunded.short_description = "Mark selected payments as Refunded"


@admin.register(RefundRequest)
class RefundRequestAdmin(admin.ModelAdmin):
    list_display = ['payment', 'reason', 'refund_amount', 'status', 'created_at']
    list_filter = ['reason', 'status', 'created_at']
    search_fields = ['payment__order__order_number', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Refund Information', {
            'fields': ('payment', 'reason', 'refund_amount', 'status')
        }),
        ('Customer Details', {
            'fields': ('description',)
        }),
        ('Admin Response', {
            'fields': ('admin_notes', 'rejected_reason'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_refund', 'reject_refund', 'mark_as_processed']
    
    def approve_refund(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_refund.short_description = "Approve selected refunds"
    
    def reject_refund(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_refund.short_description = "Reject selected refunds"
    
    def mark_as_processed(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='PROCESSED', processed_at=timezone.now())
    mark_as_processed.short_description = "Mark selected refunds as Processed"
