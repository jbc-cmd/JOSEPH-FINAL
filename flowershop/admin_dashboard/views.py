import csv

from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Count, Max, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import UserProfile
from configurations.models import GeneralConfig, ServiceConfig
from orders.models import Order
from payments.models import RefundRequest
from products.models import Category, Product

from .forms import (
    AdminProfileForm,
    AdminChangeOwnPasswordForm,
    AdminResetPasswordForm,
    AdminSettingForm,
    CategoryAdminForm,
    GeneralConfigForm,
    OrderStatusForm,
    ProductAdminForm,
    RefundStatusForm,
    ServiceConfigForm,
    UserStatusForm,
)
from .models import AdminActivityLog, LoginAttempt
from .services import (
    get_inventory_snapshot,
    get_notifications,
    get_overview_metrics,
    get_product_performance,
    get_recent_activity,
    get_recent_orders,
    get_report_context,
    get_sales_chart_data,
    get_security_snapshot,
    get_settings_context,
)
from .utils import admin_redirect_response, admin_required, build_simple_pdf, get_admin_settings, log_admin_activity


def _ensure_admin(request):
    if not request.user.is_authenticated:
        return redirect(f"/accounts/login/?next={request.get_full_path()}")
    if not (request.user.is_staff or request.user.is_superuser):
        return admin_redirect_response(request)
    return None


def _admin_context(request, **extra):
    control_center_summary = {
        'orders': Order.objects.count(),
        'customers': User.objects.filter(is_staff=False, is_superuser=False).count(),
        'products': Product.objects.count(),
        'pending_orders': Order.objects.filter(status='PENDING').count(),
    }
    return {
        'admin_settings': get_admin_settings(),
        'notification_items': get_notifications()[:5],
        'audit_log_count': AdminActivityLog.objects.count(),
        'control_center_summary': control_center_summary,
        **extra,
    }


def _paginate(request, queryset, per_page=10):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get('page'))


@admin_required
def dashboard_home(request):
    context = _admin_context(
        request,
        page_title='Overview',
        metrics=get_overview_metrics(),
        recent_activity=get_recent_activity(),
        recent_orders=get_recent_orders(),
        recent_users=User.objects.order_by('-date_joined')[:6],
        recent_products=Product.objects.select_related('category').order_by('-updated_at')[:6],
        low_stock_products=Product.objects.filter(
            stock_quantity__lte=get_admin_settings().low_stock_threshold,
            stock_quantity__gt=0,
        ).order_by('stock_quantity', 'name')[:6],
        pending_refunds=RefundRequest.objects.select_related('payment__order').filter(status='PENDING').order_by('-created_at')[:6],
        sales_chart_data=get_sales_chart_data(),
        dashboard_date=timezone.localdate(),
        orders_today=Order.objects.filter(created_at__date=timezone.localdate()).count(),
        security_snapshot=get_security_snapshot(),
    )
    return render(request, 'admin_dashboard/dashboard.html', context)


@admin_required
def user_list(request):
    search = request.GET.get('search', '').strip()
    role = request.GET.get('role', '').strip()
    account_status = request.GET.get('account_status', '').strip()
    date_filter = request.GET.get('date', '').strip()

    users = (
        User.objects
        .select_related('profile')
        .annotate(order_count=Count('orders'), last_order_at=Max('orders__created_at'))
        .order_by('-date_joined')
    )

    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search) |
            Q(email__icontains=search)
        )

    if role == 'admin_superuser':
        users = users.filter(is_superuser=True)
    elif role == 'staff':
        users = users.filter(is_staff=True, is_superuser=False)
    elif role == 'customer':
        users = users.filter(is_staff=False, is_superuser=False)

    if account_status == 'active':
        users = users.filter(is_active=True)
    elif account_status == 'inactive':
        users = users.filter(is_active=False)

    if date_filter:
        users = users.filter(date_joined__date=date_filter)

    user_page = _paginate(request, users, per_page=12)
    for managed_user in user_page.object_list:
        UserProfile.objects.get_or_create(user=managed_user)

    context = _admin_context(
        request,
        page_title='Users',
        user_page=user_page,
        search=search,
        role=role,
        account_status=account_status,
        date_filter=date_filter,
    )
    return render(request, 'admin_dashboard/users.html', context)


@admin_required
def user_detail(request, user_id):
    managed_user = get_object_or_404(User, pk=user_id)
    UserProfile.objects.get_or_create(user=managed_user)
    managed_user = User.objects.select_related('profile').get(pk=user_id)
    status_form = UserStatusForm(instance=managed_user)
    reset_form = AdminResetPasswordForm(user=managed_user)
    login_history = managed_user.login_attempts.all()[:20]
    purchase_history = managed_user.orders.prefetch_related('items').all()[:20]

    context = _admin_context(
        request,
        page_title='User Details',
        managed_user=managed_user,
        status_form=status_form,
        reset_form=reset_form,
        login_history=login_history,
        purchase_history=purchase_history,
    )
    return render(request, 'admin_dashboard/user_detail.html', context)


@admin_required
@require_POST
def toggle_user_status(request, user_id):
    managed_user = get_object_or_404(User, pk=user_id)
    if managed_user == request.user:
        messages.error(request, 'You cannot suspend your own admin account.')
        return redirect('admin_dashboard:user_detail', user_id=user_id)

    managed_user.is_active = not managed_user.is_active
    managed_user.save(update_fields=['is_active'])
    action = 'Activated' if managed_user.is_active else 'Suspended'
    log_admin_activity(
        request,
        category='USER',
        action=f'{action} user',
        description=f'{action} account for {managed_user.username}.',
        target_type='User',
        target_id=managed_user.pk,
        target_label=managed_user.username,
    )
    messages.success(request, f'{managed_user.username} is now {action.lower()}.')
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@admin_required
@require_POST
def delete_user(request, user_id):
    managed_user = get_object_or_404(User, pk=user_id)
    if managed_user == request.user:
        messages.error(request, 'You cannot delete your own admin account.')
        return redirect('admin_dashboard:user_detail', user_id=user_id)

    username = managed_user.username
    managed_user.delete()
    log_admin_activity(
        request,
        category='USER',
        action='Deleted user',
        description=f'Deleted user account for {username}.',
        target_type='User',
        target_label=username,
    )
    messages.success(request, f'{username} has been deleted.')
    return redirect('admin_dashboard:users')


@admin_required
@require_POST
def reset_user_password(request, user_id):
    managed_user = get_object_or_404(User, pk=user_id)
    form = AdminResetPasswordForm(managed_user, request.POST)
    if form.is_valid():
        form.save()
        log_admin_activity(
            request,
            category='USER',
            action='Reset user password',
            description=f'Reset password for {managed_user.username}.',
            target_type='User',
            target_id=managed_user.pk,
            target_label=managed_user.username,
        )
        generated = getattr(form, 'generated_password', '')
        if generated:
            messages.success(request, f'Temporary password for {managed_user.username}: {generated}')
        else:
            messages.success(request, f'Password updated for {managed_user.username}.')
    else:
        messages.error(request, 'Please correct the password form and try again.')
    return redirect('admin_dashboard:user_detail', user_id=user_id)


@admin_required
def security_dashboard(request):
    search = request.GET.get('q', '').strip()
    login_status = request.GET.get('status', '').strip()

    attempts = LoginAttempt.objects.select_related('user').all()
    if search:
        attempts = attempts.filter(
            Q(username__icontains=search) |
            Q(ip_address__icontains=search) |
            Q(path__icontains=search)
        )
    if login_status in {'SUCCESS', 'FAILED'}:
        attempts = attempts.filter(status=login_status)

    context = _admin_context(
        request,
        page_title='Security',
        snapshot=get_security_snapshot(),
        attempts_page=_paginate(request, attempts, per_page=20),
        search=search,
        login_status=login_status,
    )
    return render(request, 'admin_dashboard/security.html', context)


@admin_required
def product_list(request):
    search = request.GET.get('search', '').strip()
    availability = request.GET.get('availability', '').strip()
    products = get_product_performance()
    if search:
        products = products.filter(name__icontains=search)
    if availability == 'featured':
        products = products.filter(is_featured=True)
    elif availability == 'out':
        products = products.filter(stock_quantity=0)
    elif availability == 'inactive':
        products = products.filter(is_available=False)
    elif availability == 'low_stock':
        products = products.filter(
            stock_quantity__lte=get_admin_settings().low_stock_threshold,
            stock_quantity__gt=0,
        )

    context = _admin_context(
        request,
        page_title='Products',
        product_page=_paginate(request, products, per_page=12),
        search=search,
        availability=availability,
    )
    return render(request, 'admin_dashboard/products.html', context)


@admin_required
def product_create(request):
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            log_admin_activity(
                request,
                category='PRODUCT',
                action='Created product',
                description=f'Created product {product.name}.',
                target_type='Product',
                target_id=product.pk,
                target_label=product.name,
            )
            messages.success(request, 'Product created successfully.')
            return redirect('admin_dashboard:products')
    else:
        form = ProductAdminForm()

    return render(request, 'admin_dashboard/product_form.html', _admin_context(request, page_title='Add Product', form=form, mode='create'))


@admin_required
def product_edit(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = ProductAdminForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            product = form.save()
            log_admin_activity(
                request,
                category='PRODUCT',
                action='Updated product',
                description=f'Updated product {product.name}.',
                target_type='Product',
                target_id=product.pk,
                target_label=product.name,
            )
            messages.success(request, 'Product updated successfully.')
            return redirect('admin_dashboard:products')
    else:
        form = ProductAdminForm(instance=product)

    return render(request, 'admin_dashboard/product_form.html', _admin_context(request, page_title='Edit Product', form=form, product=product, mode='edit'))


@admin_required
@require_POST
def product_delete(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    name = product.name
    product.delete()
    log_admin_activity(
        request,
        category='PRODUCT',
        action='Deleted product',
        description=f'Deleted product {name}.',
        target_type='Product',
        target_label=name,
    )
    messages.success(request, f'{name} has been deleted.')
    return redirect('admin_dashboard:products')


@admin_required
def category_list(request):
    context = _admin_context(
        request,
        page_title='Categories',
        categories=Category.objects.order_by('name'),
    )
    return render(request, 'admin_dashboard/categories.html', context)


@admin_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            log_admin_activity(
                request,
                category='PRODUCT',
                action='Created category',
                description=f'Created category {category.name}.',
                target_type='Category',
                target_id=category.pk,
                target_label=category.name,
            )
            messages.success(request, 'Category created successfully.')
            return redirect('admin_dashboard:categories')
    else:
        form = CategoryAdminForm()
    return render(request, 'admin_dashboard/category_form.html', _admin_context(request, page_title='Add Category', form=form, mode='create'))


@admin_required
def category_edit(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        form = CategoryAdminForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            category = form.save()
            log_admin_activity(
                request,
                category='PRODUCT',
                action='Updated category',
                description=f'Updated category {category.name}.',
                target_type='Category',
                target_id=category.pk,
                target_label=category.name,
            )
            messages.success(request, 'Category updated successfully.')
            return redirect('admin_dashboard:categories')
    else:
        form = CategoryAdminForm(instance=category)
    return render(request, 'admin_dashboard/category_form.html', _admin_context(request, page_title='Edit Category', form=form, category=category, mode='edit'))


@admin_required
@require_POST
def category_delete(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    name = category.name
    category.delete()
    log_admin_activity(
        request,
        category='PRODUCT',
        action='Deleted category',
        description=f'Deleted category {name}.',
        target_type='Category',
        target_label=name,
    )
    messages.success(request, f'{name} has been deleted.')
    return redirect('admin_dashboard:categories')


@admin_required
def order_list(request):
    search = request.GET.get('search', '').strip()
    status = request.GET.get('status', '').strip()
    payment_status = request.GET.get('payment_status', '').strip()
    orders = Order.objects.select_related('user', 'payment').order_by('-created_at')
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(customer_name__icontains=search) |
            Q(customer_email__icontains=search)
        )
    if status:
        orders = orders.filter(status=status)
    if payment_status:
        orders = orders.filter(payment_status=payment_status)

    context = _admin_context(
        request,
        page_title='Orders',
        order_page=_paginate(request, orders, per_page=15),
        search=search,
        status=status,
        payment_status=payment_status,
    )
    return render(request, 'admin_dashboard/orders.html', context)


@admin_required
def order_detail(request, order_id):
    order = get_object_or_404(Order.objects.select_related('user', 'payment'), pk=order_id)
    refund_requests = RefundRequest.objects.filter(payment__order=order)
    context = _admin_context(
        request,
        page_title='Order Details',
        order=order,
        status_form=OrderStatusForm(instance=order),
        refund_forms=[(refund, RefundStatusForm(instance=refund, prefix=f'refund-{refund.pk}')) for refund in refund_requests],
    )
    return render(request, 'admin_dashboard/order_detail.html', context)


@admin_required
@require_POST
def update_order_status(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    form = OrderStatusForm(request.POST, instance=order)
    if form.is_valid():
        updated_order = form.save()
        log_admin_activity(
            request,
            category='ORDER',
            action='Updated order status',
            description=f'Updated {updated_order.order_number} to {updated_order.status}.',
            target_type='Order',
            target_id=updated_order.pk,
            target_label=updated_order.order_number,
            metadata={'payment_status': updated_order.payment_status},
        )
        messages.success(request, 'Order updated successfully.')
    else:
        messages.error(request, 'Please review the order status form.')
    return redirect('admin_dashboard:order_detail', order_id=order_id)


@admin_required
@require_POST
def update_refund_status(request, order_id, refund_id):
    refund = get_object_or_404(RefundRequest, pk=refund_id, payment__order_id=order_id)
    form = RefundStatusForm(request.POST, instance=refund, prefix=f'refund-{refund.pk}')
    if form.is_valid():
        refund = form.save()
        log_admin_activity(
            request,
            category='ORDER',
            action='Updated refund request',
            description=f'Updated refund for {refund.payment.order.order_number} to {refund.status}.',
            target_type='RefundRequest',
            target_id=refund.pk,
            target_label=refund.payment.order.order_number,
        )
        messages.success(request, 'Refund request updated.')
    else:
        messages.error(request, 'Please review the refund form.')
    return redirect('admin_dashboard:order_detail', order_id=order_id)


@admin_required
def report_list(request):
    return render(request, 'admin_dashboard/reports.html', _admin_context(request, page_title='Reports', **get_report_context()))


@admin_required
def inventory_dashboard(request):
    return render(request, 'admin_dashboard/inventory.html', _admin_context(request, page_title='Inventory', snapshot=get_inventory_snapshot()))


@admin_required
def notification_center(request):
    return render(request, 'admin_dashboard/notifications.html', _admin_context(request, page_title='Notifications', notifications=get_notifications()))


@admin_required
def settings_dashboard(request):
    general_config, _ = GeneralConfig.objects.get_or_create(pk=1)
    admin_settings = get_admin_settings()
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    selected_service = None

    if request.method == 'POST':
        section = request.POST.get('section')
        if section == 'general':
            form = GeneralConfigForm(request.POST, instance=general_config)
            if form.is_valid():
                form.save()
                log_admin_activity(request, category='SETTINGS', action='Updated website settings', description='Updated general website settings.')
                messages.success(request, 'Website settings updated.')
                return redirect('admin_dashboard:settings')
        elif section == 'admin':
            form = AdminSettingForm(request.POST, instance=admin_settings)
            if form.is_valid():
                form.save()
                log_admin_activity(request, category='SETTINGS', action='Updated admin settings', description='Updated tax, session, and alert settings.')
                messages.success(request, 'Admin settings updated.')
                return redirect('admin_dashboard:settings')
        elif section == 'profile':
            form = AdminProfileForm(request.POST, request.FILES, instance=profile, user=request.user)
            if form.is_valid():
                request.user.first_name = form.cleaned_data['first_name']
                request.user.last_name = form.cleaned_data['last_name']
                request.user.email = form.cleaned_data['email']
                request.user.save(update_fields=['first_name', 'last_name', 'email'])
                form.save()
                log_admin_activity(request, category='SETTINGS', action='Updated admin profile', description='Updated admin profile details.')
                messages.success(request, 'Admin profile updated.')
                return redirect('admin_dashboard:settings')
        elif section == 'password':
            form = AdminChangeOwnPasswordForm(request.user, request.POST)
            if form.is_valid():
                form.save()
                update_session_auth_hash(request, request.user)
                log_admin_activity(request, category='SETTINGS', action='Changed admin password', description='Changed the current admin password.')
                messages.success(request, 'Password updated successfully.')
                return redirect('admin_dashboard:settings')
        elif section == 'service':
            service_id = request.POST.get('service_id')
            selected_service = get_object_or_404(ServiceConfig, pk=service_id) if service_id else None
            form = ServiceConfigForm(request.POST, instance=selected_service)
            if form.is_valid():
                saved = form.save()
                log_admin_activity(
                    request,
                    category='SETTINGS',
                    action='Updated payment settings',
                    description=f'Updated service configuration for {saved.service_name}.',
                    target_type='ServiceConfig',
                    target_id=saved.pk,
                    target_label=saved.service_name,
                )
                messages.success(request, 'Service settings saved.')
                return redirect('admin_dashboard:settings')
        messages.error(request, 'Please review the settings form and try again.')
    else:
        service_id = request.GET.get('service')
        if service_id:
            selected_service = get_object_or_404(ServiceConfig, pk=service_id)

    context = _admin_context(
        request,
        page_title='Settings',
        general_form=GeneralConfigForm(instance=general_config),
        admin_form=AdminSettingForm(instance=admin_settings),
        profile_form=AdminProfileForm(instance=profile, user=request.user),
        password_form=AdminChangeOwnPasswordForm(request.user),
        service_form=ServiceConfigForm(instance=selected_service),
        selected_service=selected_service,
        service_configs=ServiceConfig.objects.order_by('service_name'),
    )
    return render(request, 'admin_dashboard/settings.html', context)


@admin_required
def audit_logs(request):
    logs = AdminActivityLog.objects.select_related('admin_user').order_by('-created_at')
    category = request.GET.get('category', '').strip()
    if category:
        logs = logs.filter(category=category)
    context = _admin_context(
        request,
        page_title='Audit Logs',
        log_page=_paginate(request, logs, per_page=20),
        category=category,
    )
    return render(request, 'admin_dashboard/audit_logs.html', context)


@admin_required
def export_orders_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="orders-{timezone.now().date()}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Order Number', 'Customer', 'Email', 'Status', 'Payment Status', 'Total', 'Created'])
    for order in Order.objects.order_by('-created_at'):
        writer.writerow([order.order_number, order.customer_name, order.customer_email, order.status, order.payment_status, order.total_amount, order.created_at.isoformat()])
    log_admin_activity(request, category='REPORT', action='Exported orders CSV', description='Downloaded order export in CSV format.')
    return response


@admin_required
def export_orders_pdf(request):
    lines = [
        f'{order.order_number} | {order.customer_name} | {order.status} | {order.payment_status} | {order.total_amount}'
        for order in Order.objects.order_by('-created_at')[:40]
    ]
    response = HttpResponse(build_simple_pdf('Orders Export', lines), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="orders-{timezone.now().date()}.pdf"'
    log_admin_activity(request, category='REPORT', action='Exported orders PDF', description='Downloaded order export in PDF format.')
    return response


@admin_required
def export_reports_csv(request):
    context = get_report_context()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="sales-report-{timezone.now().date()}.csv"'
    writer = csv.writer(response)
    writer.writerow(['Metric', 'Value'])
    for key, value in context['overview'].items():
        writer.writerow([key, value])
    writer.writerow([])
    writer.writerow(['Best Selling Products', 'Units Sold'])
    for product in context['best_selling']:
        writer.writerow([product.name, product.total_units])
    writer.writerow([])
    writer.writerow(['Low Selling Products', 'Units Sold'])
    for product in context['low_selling']:
        writer.writerow([product.name, product.total_units])
    log_admin_activity(request, category='REPORT', action='Exported report CSV', description='Downloaded sales report in CSV format.')
    return response


@admin_required
def export_reports_pdf(request):
    context = get_report_context()
    lines = [f'{key.replace("_", " ").title()}: {value}' for key, value in context['overview'].items()]
    lines.append('Best sellers:')
    lines.extend([f'{product.name} - {product.total_units} units' for product in context['best_selling']])
    response = HttpResponse(build_simple_pdf('Sales Report Export', lines), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="sales-report-{timezone.now().date()}.pdf"'
    log_admin_activity(request, category='REPORT', action='Exported report PDF', description='Downloaded sales report in PDF format.')
    return response
