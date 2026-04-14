from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.urls import reverse
from .models import Order, OrderItem, OrderTracking
from cart.views import get_or_create_cart
from cart.models import CartItem, Cart
from products.models import Product
from custom_bouquet.models import Bouquet
from delivery.models import DeliveryTimeWindow, Delivery
from payments.models import Payment
from django.utils import timezone
import uuid
import re

ORDER_TIMELINE = [
    ('PENDING', 'Order Placed', 'Your order has been received and queued for our team.', 'fa-receipt'),
    ('PROCESSING', 'Processing', 'We are confirming your order details and delivery schedule.', 'fa-credit-card'),
    ('PREPARING', 'Preparing Bouquet', 'Your flowers are currently being arranged by our florist.', 'fa-spa'),
    ('OUT_FOR_DELIVERY', 'Out for Delivery', 'Your bouquet is on the way to the delivery address.', 'fa-truck'),
    ('DELIVERED', 'Delivered', 'Your flowers have arrived at their destination.', 'fa-heart'),
]


def _normalize_order_number(raw_value):
    if not raw_value:
        return ''

    normalized = raw_value.strip().upper()
    match = re.search(r'ORD-\d{8}-[A-Z0-9]+', normalized)
    if match:
        return match.group(0)

    return normalized.replace(' ', '')


def _status_theme(status):
    themes = {
        'PENDING': {
            'accent': 'pink',
            'icon': 'fa-receipt',
            'title': 'Order received',
            'description': 'We have your flower order and will start reviewing it shortly.',
            'panel': 'border-pink-100 bg-gradient-to-br from-pink-50 via-white to-rose-50',
        },
        'PROCESSING': {
            'accent': 'amber',
            'icon': 'fa-seedling',
            'title': 'Processing your order',
            'description': 'We are confirming your recipient details and delivery schedule, and preparing your order for the florist.',
            'panel': 'border-amber-100 bg-gradient-to-br from-amber-50 via-white to-rose-50',
        },
        'PREPARING': {
            'accent': 'fuchsia',
            'icon': 'fa-spa',
            'title': 'Preparing your bouquet',
            'description': 'Your flowers are currently being arranged by our florist.',
            'panel': 'border-fuchsia-100 bg-gradient-to-br from-fuchsia-50 via-white to-pink-50',
        },
        'OUT_FOR_DELIVERY': {
            'accent': 'sky',
            'icon': 'fa-truck-fast',
            'title': 'Out for delivery',
            'description': 'Your flowers are on the way and will arrive during the scheduled delivery window.',
            'panel': 'border-sky-100 bg-gradient-to-br from-sky-50 via-white to-pink-50',
        },
        'DELIVERED': {
            'accent': 'emerald',
            'icon': 'fa-circle-check',
            'title': 'Delivered successfully',
            'description': 'Your bouquet has been delivered. We hope it made someone smile.',
            'panel': 'border-emerald-100 bg-gradient-to-br from-emerald-50 via-white to-pink-50',
        },
        'CANCELLED': {
            'accent': 'rose',
            'icon': 'fa-ban',
            'title': 'Order cancelled',
            'description': 'This order is no longer active. Please contact support if you need help.',
            'panel': 'border-rose-100 bg-gradient-to-br from-rose-50 via-white to-pink-50',
        },
    }
    return themes.get(status, themes['PENDING'])


def _build_timeline(order):
    status_order = [step[0] for step in ORDER_TIMELINE]
    current_index = status_order.index(order.status) if order.status in status_order else 0
    timeline = []

    for index, (code, title, description, icon) in enumerate(ORDER_TIMELINE):
        if order.status == 'CANCELLED':
            state = 'completed' if code == 'PENDING' else 'upcoming'
        elif order.status == 'DELIVERED':
            state = 'current' if code == 'DELIVERED' else 'completed'
        elif index < current_index:
            state = 'completed'
        elif index == current_index:
            state = 'current'
        else:
            state = 'upcoming'

        timeline.append({
            'code': code,
            'title': title,
            'description': description,
            'icon': icon,
            'state': state,
            'is_last': index == len(ORDER_TIMELINE) - 1,
        })

    return timeline


def _format_delivery_window(time_window):
    if not time_window:
        return 'Delivery window to be confirmed'
    return f"{time_window.start_time.strftime('%I:%M %p').lstrip('0')} - {time_window.end_time.strftime('%I:%M %p').lstrip('0')}"


def _estimated_arrival_text(order):
    if not order.delivery_time_window:
        return 'Delivery timing will be confirmed soon.'

    window_text = _format_delivery_window(order.delivery_time_window)
    today = timezone.localdate()
    if order.status == 'DELIVERED':
        return f"Delivered on {order.delivery_date.strftime('%B %d, %Y')}."
    if order.delivery_date == today:
        return f"Arriving today between {window_text}."
    return f"Scheduled for {order.delivery_date.strftime('%B %d, %Y')} between {window_text}."


def _can_manage_order(request, order):
    if request.user.is_authenticated and order.user == request.user:
        return True
    return request.session.get('order_id') == order.id


def _get_checkout_delivery_address(user):
    """Return the user's default saved delivery address, or the first available one."""
    if not user.is_authenticated:
        return None
    return user.delivery_addresses.filter(is_default=True).first() or user.delivery_addresses.first()


def checkout(request):
    """Checkout page with order summary."""
    direct_purchase = request.session.get('direct_purchase')

    if direct_purchase:
        # Direct purchase from product detail page
        items = []
        subtotal = 0

        if direct_purchase['type'] == 'product':
            product = get_object_or_404(Product, id=direct_purchase['product_id'])
            item_subtotal = float(product.price) * direct_purchase['quantity']
            subtotal = item_subtotal
            items = [{
                'get_item_name': product.name,
                'quantity': direct_purchase['quantity'],
                'get_subtotal': item_subtotal,
                'price_at_purchase': product.price,
                'product_id': product.id,
                'is_direct_purchase': True
            }]
        elif direct_purchase['type'] == 'bouquet':
            bouquet = get_object_or_404(Bouquet, id=direct_purchase['bouquet_id'])
            item_subtotal = float(bouquet.total_price) * direct_purchase['quantity']
            subtotal = item_subtotal
            items = [{
                'get_item_name': bouquet.name,
                'quantity': direct_purchase['quantity'],
                'get_subtotal': item_subtotal,
                'price_at_purchase': bouquet.total_price,
                'bouquet_id': bouquet.id,
                'is_direct_purchase': True
            }]
    else:
        # Regular cart checkout
        cart = get_or_create_cart(request)

        if not cart.items.exists():
            messages.error(request, 'Your cart is empty!')
            return redirect('cart:cart')

        items = list(cart.items.all())
        subtotal = cart.get_total_price()

    if not request.user.is_authenticated:
        messages.error(request, 'Please sign in before proceeding to checkout.')
        return redirect(f"{reverse('accounts:login')}?next={request.path}")

    saved_address = _get_checkout_delivery_address(request.user)
    if not saved_address:
        messages.error(request, 'Please add or update your delivery address in your profile before checkout.')
        return redirect('accounts:profile')

    delivery_windows = DeliveryTimeWindow.objects.filter(is_available=True)

    # Create a temporary cart for calculating fees
    temp_cart = Cart(id=0)
    temp_cart.items_total = subtotal
    delivery_fee = temp_cart.get_delivery_fee()
    total = subtotal + delivery_fee

    context = {
        'items': items,
        'delivery_windows': delivery_windows,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'saved_address': saved_address,
        'is_direct_purchase': bool(direct_purchase),
    }

    return render(request, 'orders/checkout.html', context)


@require_POST
def create_order(request):
    """Create order from checkout."""
    direct_purchase = request.session.get('direct_purchase')

    if direct_purchase:
        # Direct purchase from product detail page
        if direct_purchase['type'] == 'product':
            product = get_object_or_404(Product, id=direct_purchase['product_id'])
            subtotal = float(product.price) * direct_purchase['quantity']
        elif direct_purchase['type'] == 'bouquet':
            bouquet = get_object_or_404(Bouquet, id=direct_purchase['bouquet_id'])
            subtotal = float(bouquet.total_price) * direct_purchase['quantity']
        else:
            return JsonResponse({'success': False, 'message': 'Invalid purchase type'})
    else:
        # Regular cart checkout
        cart = get_or_create_cart(request)

        if not cart.items.exists():
            return JsonResponse({'success': False, 'message': 'Cart is empty'})

        subtotal = cart.get_total_price()

    if not request.user.is_authenticated:
        return JsonResponse({
            'success': False,
            'message': 'Please sign in before proceeding to checkout.',
            'redirect_url': f"{reverse('accounts:login')}?next={reverse('orders:checkout')}"
        })

    try:
        saved_address = _get_checkout_delivery_address(request.user)
        if not saved_address:
            return JsonResponse({
                'success': False,
                'message': 'Please add or update your delivery address in your profile before checkout.',
                'redirect_url': reverse('accounts:profile')
            })

        # Get form data
        customer_name = saved_address.recipient_name
        customer_email = request.user.email
        customer_phone = saved_address.phone_number
        delivery_address = saved_address.address
        delivery_city = saved_address.city
        delivery_postal_code = saved_address.postal_code or ''
        delivery_date_str = request.POST.get('delivery_date')
        delivery_time_window_id = request.POST.get('delivery_time_window')
        gift_message = request.POST.get('gift_message', '')
        anonymous_sender = request.POST.get('anonymous_sender') == 'on'
        special_instructions = request.POST.get('special_instructions', '')

        # Parse delivery date
        from datetime import datetime
        delivery_date = datetime.strptime(delivery_date_str, '%Y-%m-%d').date()

        # Get delivery time window
        delivery_time_window = get_object_or_404(DeliveryTimeWindow, id=delivery_time_window_id)

        # Calculate delivery fee and total
        temp_cart = Cart(id=0)
        temp_cart.items_total = subtotal
        delivery_fee = temp_cart.get_delivery_fee()
        total_amount = subtotal + delivery_fee

        # Create order
        order = Order.objects.create(
            user=request.user if request.user.is_authenticated else None,
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            delivery_address=delivery_address,
            delivery_city=delivery_city,
            delivery_postal_code=delivery_postal_code,
            delivery_date=delivery_date,
            delivery_time_window=delivery_time_window,
            gift_message=gift_message,
            anonymous_sender=anonymous_sender,
            special_instructions=special_instructions,
            subtotal=subtotal,
            delivery_fee=delivery_fee,
            total_amount=total_amount,
        )

        # Create order items
        if direct_purchase:
            if direct_purchase['type'] == 'product':
                product = get_object_or_404(Product, id=direct_purchase['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=direct_purchase['quantity'],
                    price=product.price,
                    subtotal=float(product.price) * direct_purchase['quantity']
                )
            elif direct_purchase['type'] == 'bouquet':
                bouquet = get_object_or_404(Bouquet, id=direct_purchase['bouquet_id'])
                OrderItem.objects.create(
                    order=order,
                    bouquet=bouquet,
                    quantity=direct_purchase['quantity'],
                    price=bouquet.total_price,
                    subtotal=float(bouquet.total_price) * direct_purchase['quantity']
                )
        else:
            # Regular cart items
            cart = get_or_create_cart(request)
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    bouquet=cart_item.bouquet,
                    quantity=cart_item.quantity,
                    price=cart_item.price_at_purchase,
                    subtotal=cart_item.get_subtotal()
                )

        # Create delivery record
        delivery = Delivery.objects.create(
            delivery_number=f"DEL-{uuid.uuid4().hex[:10].upper()}",
            status='PENDING',
            delivery_address=delivery_address,
            recipient_name=customer_name,
            recipient_phone=customer_phone,
            delivery_date=delivery_date,
            delivery_time_window=delivery_time_window,
        )
        order.delivery = delivery
        order.save()

        # Create order tracking
        OrderTracking.objects.create(
            order=order,
            track_by_order_number=order.order_number,
            track_by_email=customer_email
        )

        # Create payment record
        Payment.objects.create(
            order=order,
            payment_method=request.POST.get('payment_method', 'COD'),
            amount=order.total_amount,
            status='PENDING'
        )

        # Clear appropriate cart/session
        if direct_purchase:
            # Clear direct purchase from session
            del request.session['direct_purchase']
        else:
            # Clear regular cart
            cart.items.all().delete()

        # Store order in session for confirmation page
        request.session['order_id'] = order.id

        return JsonResponse({
            'success': True,
            'order_number': order.order_number,
            'redirect_url': f'/orders/{order.id}/confirmation/'
        })

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})


def order_confirmation(request, order_id):
    """Order confirmation page."""
    order = get_object_or_404(Order, id=order_id)
    
    # Security check - only owner can view
    if request.user.is_authenticated and order.user != request.user:
        if request.session.get('order_id') != order_id:
            messages.error(request, 'You do not have permission to view this order')
            return redirect('products:home')
    
    context = {
        'order': order,
        'items': order.items.all(),
    }
    return render(request, 'orders/order_confirmation.html', context)


def track_order(request):
    """Order tracking page."""
    entered_order_number = ''
    entered_email = request.user.email if request.user.is_authenticated else ''

    if request.method == 'POST':
        order_number = _normalize_order_number(request.POST.get('order_number'))
        email = request.POST.get('email', '').strip()
        entered_order_number = order_number
        entered_email = email
        
        try:
            order = Order.objects.get(order_number=order_number, customer_email=email)
            return redirect('orders:order_detail', order_id=order.id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Please check your order number and email.')

    context = {
        'entered_order_number': entered_order_number,
        'entered_email': entered_email,
    }
    return render(request, 'orders/track_order.html', context)


def order_detail(request, order_id):
    """Order detail and tracking page."""
    order = get_object_or_404(Order, id=order_id)
    payment = getattr(order, 'payment', None)
    theme = _status_theme(order.status)
    cancel_deadline = order.get_cancel_deadline()
    
    context = {
        'order': order,
        'items': order.items.all(),
        'payment': payment,
        'delivery': order.delivery,
        'status_color': order.get_status_badge_color(),
        'status_summary': theme,
        'timeline_steps': _build_timeline(order),
        'estimated_arrival': _estimated_arrival_text(order),
        'delivery_window_text': _format_delivery_window(order.delivery_time_window),
        'cancel_deadline': cancel_deadline,
        'can_cancel_order': order.can_customer_cancel_now() and _can_manage_order(request, order),
        'can_request_cancellation': order.can_customer_request_cancellation() and _can_manage_order(request, order),
    }
    return render(request, 'orders/order_detail.html', context)


@require_POST
def cancel_order(request, order_id):
    """Allow customers to cancel within 5 hours or request cancellation afterwards."""
    order = get_object_or_404(Order, id=order_id)

    if not _can_manage_order(request, order):
        messages.error(request, 'You do not have permission to manage this order.')
        return redirect('products:home')

    action = request.POST.get('action')
    reason = request.POST.get('cancellation_reason', '').strip()

    if action == 'cancel' and order.can_customer_cancel_now():
        order.status = 'CANCELLED'
        order.cancelled_at = timezone.now()
        order.cancellation_requested_at = None
        order.cancellation_request_reason = ''
        order.save(update_fields=['status', 'cancelled_at', 'cancellation_requested_at', 'cancellation_request_reason', 'updated_at'])
        messages.success(request, 'Your order has been cancelled successfully.')
    elif action == 'request_cancel' and order.can_customer_request_cancellation():
        order.cancellation_requested_at = timezone.now()
        order.cancellation_request_reason = reason
        order.save(update_fields=['cancellation_requested_at', 'cancellation_request_reason', 'updated_at'])
        messages.success(request, 'Your cancellation request has been sent. Our team will review it shortly.')
    elif order.status in ['CANCELLED', 'DELIVERED']:
        messages.error(request, 'This order can no longer be cancelled.')
    elif order.cancellation_requested_at:
        messages.error(request, 'A cancellation request has already been submitted for this order.')
    else:
        messages.error(request, 'The direct cancellation window has ended. Please submit a cancellation request instead.')

    return redirect('orders:order_detail', order_id=order.id)


@login_required(login_url='accounts:login')
def my_orders(request):
    """View authenticated user's orders."""
    orders = request.user.orders.all()
    
    context = {'orders': orders}
    return render(request, 'orders/my_orders.html', context)
