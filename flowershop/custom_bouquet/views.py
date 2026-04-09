from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Bouquet, BouquetItem, BouquetSize, WrappingStyle, RibbonColor, Extra, BouquetExtra
from products.models import Flower
from cart.views import get_or_create_cart
from cart.models import CartItem
import json
import uuid


def bouquet_builder(request):
    """Main bouquet builder page."""
    sizes = BouquetSize.objects.all()
    wrapping_styles = WrappingStyle.objects.all()
    ribbon_colors = RibbonColor.objects.all()
    extras = Extra.objects.all()
    flowers = Flower.objects.filter(availability_status='IN_STOCK')
    
    context = {
        'sizes': sizes,
        'wrapping_styles': wrapping_styles,
        'ribbon_colors': ribbon_colors,
        'extras': extras,
        'flowers': flowers,
    }
    return render(request, 'custom_bouquet/builder.html', context)


def get_bouquet_pricing(request):
    """Calculate bouquet pricing (AJAX)."""
    try:
        size_id = request.GET.get('size_id')
        wrapping_id = request.GET.get('wrapping_id')
        ribbon_id = request.GET.get('ribbon_id')
        flower_ids = request.GET.getlist('flower_ids')
        extra_ids = request.GET.getlist('extra_ids')
        
        size = BouquetSize.objects.get(id=size_id)
        wrapping = WrappingStyle.objects.get(id=wrapping_id)
        ribbon = RibbonColor.objects.get(id=ribbon_id)
        
        flowers_price = 0
        for flower_id in flower_ids:
            flower = Flower.objects.get(id=flower_id)
            flowers_price += float(flower.price)
        
        extras_price = 0
        for extra_id in extra_ids:
            extra = Extra.objects.get(id=extra_id)
            extras_price += float(extra.price)
        
        total = float(size.base_price) + float(wrapping.price) + float(ribbon.price) + flowers_price + extras_price
        
        return JsonResponse({
            'success': True,
            'size_price': float(size.base_price),
            'wrapping_price': float(wrapping.price),
            'ribbon_price': float(ribbon.price),
            'flowers_price': flowers_price,
            'extras_price': extras_price,
            'total': total,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def save_custom_bouquet(request):
    """Save custom bouquet to cart."""
    try:
        data = json.loads(request.body) if request.body.startswith(b'{') else request.POST
        
        name = data.get('name', f'Custom Bouquet {uuid.uuid4().hex[:4].upper()}')
        size_id = data.get('size_id')
        wrapping_id = data.get('wrapping_id')
        ribbon_id = data.get('ribbon_id')
        flowers_data = data.get('flowers', [])  # List of {'flower_id': ..., 'quantity': ...}
        extras_data = data.get('extras', [])
        personal_message = data.get('personal_message', '')
        
        # Create bouquet
        size = BouquetSize.objects.get(id=size_id)
        wrapping = WrappingStyle.objects.get(id=wrapping_id)
        ribbon = RibbonColor.objects.get(id=ribbon_id)
        
        # Calculate total price
        flowers_price = 0
        extras_price = 0
        
        bouquet = Bouquet.objects.create(
            name=name,
            size=size,
            wrapping=wrapping,
            ribbon_color=ribbon,
            personal_message=personal_message,
            base_price=size.base_price,
            total_price=0,  # Will be calculated below
        )
        
        # Add flowers to bouquet
        for flower_data in flowers_data:
            flower = Flower.objects.get(id=flower_data['flower_id'])
            quantity = int(flower_data.get('quantity', 1))
            
            BouquetItem.objects.create(
                bouquet=bouquet,
                flower=flower,
                quantity=quantity,
                price_per_unit=flower.price
            )
            flowers_price += float(flower.price) * quantity
        
        # Add extras to bouquet
        for extra_data in extras_data:
            extra = Extra.objects.get(id=extra_data['extra_id'])
            quantity = int(extra_data.get('quantity', 1))
            
            BouquetExtra.objects.create(
                bouquet=bouquet,
                extra=extra,
                quantity=quantity
            )
            extras_price += float(extra.price) * quantity
        
        # Calculate final total
        total = float(size.base_price) + float(wrapping.price) + float(ribbon.price) + flowers_price + extras_price
        bouquet.total_price = total
        bouquet.save()
        
        # Add to cart
        cart = get_or_create_cart(request)
        CartItem.objects.create(
            cart=cart,
            bouquet=bouquet,
            quantity=1,
            price_at_purchase=bouquet.total_price
        )
        
        return JsonResponse({
            'success': True,
            'bouquet_id': bouquet.id,
            'message': f'Custom bouquet "{name}" added to cart!',
            'cart_url': '/cart/'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def get_flower_details(request, flower_id):
    """Get flower details (AJAX)."""
    flower = get_object_or_404(Flower, id=flower_id)
    return JsonResponse({
        'id': flower.id,
        'name': flower.get_name_display(),
        'price': float(flower.price),
        'image': flower.image.url if flower.image else '',
        'color': flower.color,
        'description': flower.description,
    })
