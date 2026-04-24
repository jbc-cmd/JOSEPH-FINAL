from collections import Counter
from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.db.models import Count, DecimalField, IntegerField, Sum, Value
from django.db.models.functions import Coalesce, TruncDate, TruncMonth
from django.utils import timezone

from accounts.models import UserProfile
from configurations.models import GeneralConfig, ServiceConfig
from orders.models import Order, OrderItem
from payments.models import RefundRequest
from products.models import Category, Product

from .models import AdminActivityLog, LoginAttempt
from .utils import get_admin_settings


MONEY_ZERO = Value(Decimal('0.00'), output_field=DecimalField(max_digits=10, decimal_places=2))
INTEGER_ZERO = Value(0, output_field=IntegerField())


def get_overview_metrics():
    now = timezone.now()
    today = now.date()
    week_start = today - timedelta(days=6)
    month_start = today.replace(day=1)

    paid_orders = Order.objects.filter(payment_status='COMPLETED')
    total_sales = paid_orders.aggregate(total=Coalesce(Sum('total_amount'), MONEY_ZERO))['total']
    daily_sales = paid_orders.filter(created_at__date=today).aggregate(total=Coalesce(Sum('total_amount'), MONEY_ZERO))['total']
    weekly_sales = paid_orders.filter(created_at__date__gte=week_start).aggregate(total=Coalesce(Sum('total_amount'), MONEY_ZERO))['total']
    monthly_sales = paid_orders.filter(created_at__date__gte=month_start).aggregate(total=Coalesce(Sum('total_amount'), MONEY_ZERO))['total']

    return {
        'total_sales': total_sales,
        'daily_sales': daily_sales,
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'total_orders': Order.objects.count(),
        'total_customers': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'total_products': Product.objects.count(),
        'new_signups': User.objects.filter(date_joined__date=today).count(),
        'pending_orders': Order.objects.filter(status='PENDING').count(),
        'refund_requests': RefundRequest.objects.filter(status='PENDING').count(),
    }


def get_sales_chart_data(days=14):
    since = timezone.now() - timedelta(days=days - 1)
    series = (
        Order.objects.filter(created_at__gte=since, payment_status='COMPLETED')
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(total=Coalesce(Sum('total_amount'), MONEY_ZERO), count=Count('id'))
        .order_by('day')
    )
    return [
        {
            'label': item['day'].strftime('%b %d'),
            'sales': float(item['total']),
            'orders': item['count'],
        }
        for item in series
    ]


def get_monthly_trends(limit=6):
    rows = (
        Order.objects.filter(payment_status='COMPLETED')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Coalesce(Sum('total_amount'), MONEY_ZERO), count=Count('id'))
        .order_by('-month')[:limit]
    )
    return list(reversed([
        {
            'label': row['month'].strftime('%b %Y'),
            'revenue': float(row['total']),
            'orders': row['count'],
        }
        for row in rows
    ]))


def get_recent_activity(limit=12):
    return AdminActivityLog.objects.select_related('admin_user')[:limit]


def get_recent_orders(limit=8):
    return Order.objects.select_related('user').order_by('-created_at')[:limit]


def get_notifications():
    settings_obj = get_admin_settings()
    items = []

    if settings_obj.notify_new_orders:
        for order in Order.objects.filter(created_at__gte=timezone.now() - timedelta(days=1)).order_by('-created_at')[:5]:
            items.append({
                'kind': 'order',
                'title': f'New order {order.order_number}',
                'message': f'{order.customer_name} placed an order worth {settings_obj.currency_symbol}{order.total_amount}.',
                'created_at': order.created_at,
                'url': f'/dashboard/orders/{order.id}/',
                'action_label': 'Review order',
            })

    if settings_obj.notify_new_signups:
        for user in User.objects.filter(date_joined__gte=timezone.now() - timedelta(days=3)).order_by('-date_joined')[:5]:
            items.append({
                'kind': 'signup',
                'title': 'New customer signup',
                'message': f'{user.get_full_name() or user.username} created an account.',
                'created_at': user.date_joined,
                'url': f'/dashboard/users/{user.id}/',
                'action_label': 'View user',
            })

    if settings_obj.notify_low_stock:
        for product in Product.objects.filter(stock_quantity__lte=settings_obj.low_stock_threshold).order_by('stock_quantity', 'name')[:5]:
            items.append({
                'kind': 'inventory',
                'title': 'Low stock alert',
                'message': f'{product.name} only has {product.stock_quantity} item(s) left.',
                'created_at': product.updated_at,
                'url': f'/dashboard/products/{product.id}/edit/',
                'action_label': 'Update stock',
            })

    items.sort(key=lambda item: item['created_at'], reverse=True)
    return items[:10]


def get_security_snapshot():
    since = timezone.now() - timedelta(days=7)
    recent_attempts = LoginAttempt.objects.filter(created_at__gte=since)
    failed_attempts = recent_attempts.filter(status='FAILED')

    failed_by_ip = Counter(
        attempt.ip_address or 'Unknown'
        for attempt in failed_attempts[:200]
    )
    suspicious_ips = [
        {'ip': ip, 'count': count}
        for ip, count in failed_by_ip.items()
        if count >= 3
    ]

    return {
        'total_logins': recent_attempts.filter(status='SUCCESS').count(),
        'failed_logins': failed_attempts.count(),
        'admin_actions': AdminActivityLog.objects.filter(created_at__gte=since).count(),
        'suspicious_ips': sorted(suspicious_ips, key=lambda item: item['count'], reverse=True)[:10],
        'recent_attempts': recent_attempts.select_related('user')[:20],
    }


def get_product_performance():
    return (
        Product.objects.annotate(
            total_units=Coalesce(Sum('orderitem__quantity'), INTEGER_ZERO),
            total_revenue=Coalesce(Sum('orderitem__subtotal'), MONEY_ZERO),
        )
        .select_related('category')
        .order_by('-total_units', '-updated_at')
    )


def get_best_and_low_selling_products(limit=5):
    stats = list(
        Product.objects.annotate(total_units=Coalesce(Sum('orderitem__quantity'), INTEGER_ZERO))
        .order_by('-total_units', 'name')
    )
    best_selling = stats[:limit]
    low_selling = sorted(stats, key=lambda item: (item.total_units, item.name.lower()))[:limit]
    return best_selling, low_selling


def get_inventory_snapshot():
    threshold = get_admin_settings().low_stock_threshold
    return {
        'low_stock': Product.objects.filter(stock_quantity__lte=threshold, stock_quantity__gt=0).order_by('stock_quantity', 'name'),
        'out_of_stock': Product.objects.filter(stock_quantity=0).order_by('name'),
        'threshold': threshold,
    }


def get_report_context():
    best_selling, low_selling = get_best_and_low_selling_products()
    monthly_trends = get_monthly_trends()
    return {
        'overview': get_overview_metrics(),
        'best_selling': best_selling,
        'low_selling': low_selling,
        'monthly_trends': monthly_trends,
    }


def get_settings_context():
    general_config, _ = GeneralConfig.objects.get_or_create(pk=1)
    admin_settings = get_admin_settings()
    service_configs = ServiceConfig.objects.order_by('service_name')
    return {
        'general_config': general_config,
        'admin_settings': admin_settings,
        'service_configs': service_configs,
    }
