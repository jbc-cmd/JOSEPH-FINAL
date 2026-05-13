from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .models import Cart, CartItem
from products.models import Product
from custom_bouquet.models import Bouquet
import uuid
from urllib.parse import urlparse


def _is_cart_page_url(url):
    """Return True when a URL points to the full cart page."""
    if not url:
        return False

    return urlparse(url).path == reverse('cart:cart')


def _redirect_to_cart_drawer(request):
    """Return to the previous page and reopen the cart drawer."""
    next_url = request.POST.get('next') or request.META.get('HTTP_REFERER') or '/'
    # Don't add open_cart param if redirecting to checkout
    if 'checkout' not in next_url:
        separator = '&' if '?' in next_url else '?'
        return redirect(f'{next_url}{separator}open_cart=1')
    return redirect(next_url)


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
    # Require authentication for adding to cart
    if not request.user.is_authenticated:
        # Store the cart item data in session for later
        request.session['pending_cart_item'] = {
            'product_id': request.POST.get('product_id'),
            'bouquet_id': request.POST.get('bouquet_id'),
            'quantity': request.POST.get('quantity', '1'),
        }
        messages.warning(request, 'Please sign in to add items to your cart.')
        return redirect(f"{reverse('accounts:login')}?next={request.path}&action=add_to_cart")

    cart = get_or_create_cart(request)

    product_id = request.POST.get('product_id')
    bouquet_id = request.POST.get('bouquet_id')
    quantity = int(request.POST.get('quantity', 1))
    next_url = request.POST.get('next') or ''

    try:
        # If redirecting to checkout, store in session for direct purchase
        if 'checkout' in next_url:
            direct_purchase = None
            if product_id:
                product = get_object_or_404(Product, id=product_id)
                direct_purchase = {
                    'type': 'product',
                    'product_id': product.id,
                    'quantity': quantity,
                    'price': float(product.price)
                }

            elif bouquet_id:
                bouquet = get_object_or_404(Bouquet, id=bouquet_id)
                direct_purchase = {
                    'type': 'bouquet',
                    'bouquet_id': bouquet.id,
                    'quantity': quantity,
                    'price': float(bouquet.total_price)
                }

            if direct_purchase:
                request.session['direct_purchase'] = direct_purchase
                return redirect('orders:checkout')
            return redirect('orders:checkout')

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
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    messages.success(request, 'Item removed from cart')

    # Check if coming from cart page
    next_url = request.POST.get('next', '')
    referer = request.META.get('HTTP_REFERER', '')
    if _is_cart_page_url(next_url) or _is_cart_page_url(referer):
        return redirect('cart:cart')

    return _redirect_to_cart_drawer(request)


@require_POST
def update_cart_item(request, item_id):
    """Update quantity of cart item."""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    quantity = int(request.POST.get('quantity', 1))

    if quantity > 0:
        cart_item.quantity = quantity
        cart_item.save()
        messages.success(request, 'Cart updated')
    else:
        cart_item.delete()
        messages.success(request, 'Item removed from cart')

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': float(cart.get_total_price()),
            'cart_items': cart.get_total_items(),
            'item_subtotal': float(cart_item.get_subtotal()) if cart_item in CartItem.objects.filter(cart=cart) else 0
        })

    # Check if coming from cart page
    next_url = request.POST.get('next', '')
    referer = request.META.get('HTTP_REFERER', '')
    if _is_cart_page_url(next_url) or _is_cart_page_url(referer):
        return redirect('cart:cart')

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


def apply_pending_cart_item(request):
    """Apply pending cart item after user login."""
    if not request.user.is_authenticated:
        return redirect('accounts:login')

    pending_item = request.session.get('pending_cart_item')
    if not pending_item:
        return redirect('cart:cart')

    cart = get_or_create_cart(request)
    product_id = pending_item.get('product_id')
    bouquet_id = pending_item.get('bouquet_id')
    quantity = int(pending_item.get('quantity', 1))

    try:
        if product_id:
            product = get_object_or_404(Product, id=product_id)
            price = product.price

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

        # Clear the pending item from session
        del request.session['pending_cart_item']

    except Exception as e:
        messages.error(request, f'Error adding item: {str(e)}')

    return redirect('cart:cart')
