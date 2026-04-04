from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView
from django.http import JsonResponse
from .models import Order, OrderItem, OrderTracking
from cart.views import get_or_create_cart
from cart.models import CartItem
from delivery.models import DeliveryTimeWindow, Delivery
from payments.models import Payment
from django.utils import timezone
import uuid


def checkout(request):
    """Checkout page with order summary."""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.error(request, 'Your cart is empty!')
        return redirect('cart:cart')
    
    delivery_windows = DeliveryTimeWindow.objects.filter(is_available=True)
    
    context = {
        'cart': cart,
        'items': cart.items.all(),
        'delivery_windows': delivery_windows,
        'subtotal': cart.get_total_price(),
        'delivery_fee': cart.get_delivery_fee(),
        'total': cart.get_grand_total(),
    }
    
    if request.user.is_authenticated:
        context['user_addresses'] = request.user.delivery_addresses.all()
    
    return render(request, 'orders/checkout.html', context)


@require_POST
def create_order(request):
    """Create order from checkout."""
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        return JsonResponse({'success': False, 'message': 'Cart is empty'})
    
    try:
        # Get form data
        customer_name = request.POST.get('customer_name')
        customer_email = request.POST.get('customer_email')
        customer_phone = request.POST.get('customer_phone')
        delivery_address = request.POST.get('delivery_address')
        delivery_city = request.POST.get('delivery_city')
        delivery_postal_code = request.POST.get('delivery_postal_code', '')
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
            subtotal=cart.get_total_price(),
            delivery_fee=cart.get_delivery_fee(),
            total_amount=cart.get_grand_total(),
        )
        
        # Create order items
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
        
        # Clear cart
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
    if request.method == 'POST':
        order_number = request.POST.get('order_number')
        email = request.POST.get('email')
        
        try:
            order = Order.objects.get(order_number=order_number, customer_email=email)
            return redirect('orders:order_detail', order_id=order.id)
        except Order.DoesNotExist:
            messages.error(request, 'Order not found. Please check your order number and email.')
    
    return render(request, 'orders/track_order.html')


def order_detail(request, order_id):
    """Order detail and tracking page."""
    order = get_object_or_404(Order, id=order_id)
    
    context = {
        'order': order,
        'items': order.items.all(),
        'payment': order.payment,
        'delivery': order.delivery,
        'status_color': order.get_status_badge_color(),
    }
    return render(request, 'orders/order_detail.html', context)


@login_required(login_url='accounts:login')
def my_orders(request):
    """View authenticated user's orders."""
    orders = request.user.orders.all()
    
    context = {'orders': orders}
    return render(request, 'orders/my_orders.html', context)
