def cart_context(request):
    """Context processor to provide cart information to all templates."""
    cart = None
    total_items = 0
    
    if request.user.is_authenticated:
        try:
            from .models import Cart
            cart = Cart.objects.get(user=request.user)
            total_items = cart.get_total_items()
        except:
            pass
    elif 'session_id' in request.session:
        try:
            from .models import Cart
            cart = Cart.objects.get(session_id=request.session['session_id'])
            total_items = cart.get_total_items()
        except:
            pass
    
    return {
        'cart': cart,
        'cart_total_items': total_items
    }
