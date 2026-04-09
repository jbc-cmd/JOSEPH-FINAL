from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product
from custom_bouquet.models import Bouquet
import uuid


def _redirect_to_cart_drawer(request):
    """Return to the previous page and reopen the cart drawer."""
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    separator = '&' if '?' in next_url else '?'
    return redirect(f'{next_url}{separator}open_cart=1')


def get_or_create_cart(request):
    """Get or create cart for user or guest."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        # For guests, use session ID
        session_id = request.session.get('cart_session_id')
        if not session_id:
            session_id = str(uuid.uuid4())
            request.session['cart_session_id'] = session_id
        
        cart, created = Cart.objects.get_or_create(session_id=session_id)
    
    return cart


def cart_view(request):
    """Display shopping cart."""
    cart = get_or_create_cart(request)
    context = {
        'cart': cart,
        'items': cart.items.all(),
        'subtotal': cart.get_total_price(),
        'delivery_fee': cart.get_delivery_fee(),
        'total': cart.get_grand_total(),
    }
    return render(request, 'cart/cart.html', context)


@require_POST
def add_to_cart(request):
    """Add product or bouquet to cart."""
    cart = get_or_create_cart(request)
    
    product_id = request.POST.get('product_id')
    bouquet_id = request.POST.get('bouquet_id')
    quantity = int(request.POST.get('quantity', 1))
    
    try:
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            price = product.price
            
            # Check if already in cart
            cart_item = CartItem.objects.filter(cart=cart, product=product).first()
            if cart_item:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    quantity=quantity,
                    price_at_purchase=price
                )
            
            messages.success(request, f'{product.name} added to cart!')
        
        elif bouquet_id:
            bouquet = get_object_or_404(Bouquet, id=bouquet_id)
            price = bouquet.total_price
            
            cart_item = CartItem.objects.filter(cart=cart, bouquet=bouquet).first()
            if cart_item:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                CartItem.objects.create(
                    cart=cart,
                    bouquet=bouquet,
                    quantity=quantity,
                    price_at_purchase=price
                )
            
            messages.success(request, f'{bouquet.name} added to cart!')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total_items': cart.get_total_items(),
                'message': 'Item added to cart!'
            })

        return _redirect_to_cart_drawer(request)

    except Exception as e:
        messages.error(request, f'Error adding item: {str(e)}')
        return _redirect_to_cart_drawer(request)


@require_POST
def remove_from_cart(request, item_id):
    """Remove item from cart."""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')
    return _redirect_to_cart_drawer(request)


@require_POST
def update_cart_item(request, item_id):
    """Update quantity of cart item."""
    cart_item = get_object_or_404(CartItem, id=item_id)
    quantity = int(request.POST.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart')
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = cart_item.cart
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total_price()),
            'cart_items': cart.get_total_items(),
            'item_subtotal': float(cart_item.get_subtotal()) if cart_item in CartItem.objects.filter(cart=cart) else 0
        })
    
    return _redirect_to_cart_drawer(request)


def clear_cart(request):
    """Clear all items from cart."""
    cart = get_or_create_cart(request)
    cart.items.all().delete()
    messages.success(request, 'Cart cleared')
    return redirect('cart:cart')


def cart_count(request):
    """Return cart item count (AJAX)."""
    cart = get_or_create_cart(request)
    return JsonResponse({
        'count': cart.get_total_items(),
        'total': float(cart.get_total_price())
    })
