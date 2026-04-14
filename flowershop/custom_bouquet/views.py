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


def _resolve_selected_size(size_id, total_stems, custom_stem_count=None):
    """Resolve and validate the selected bouquet size."""
    if custom_stem_count is not None:
        if custom_stem_count < 1:
            raise ValueError('Custom size must be at least 1 flower.')
        if total_stems != custom_stem_count:
            raise ValueError(f'Your custom size expects {custom_stem_count} flowers, but you selected {total_stems}.')

        matching_size = BouquetSize.objects.filter(
            flower_count_min__lte=custom_stem_count,
            flower_count_max__gte=custom_stem_count,
        ).order_by('flower_count_min').first()

        if matching_size:
            return matching_size, True, custom_stem_count

        fallback_size = BouquetSize.objects.order_by('-flower_count_max', '-flower_count_min').first()
        if not fallback_size:
            raise ValueError('No bouquet sizes are configured yet.')

        return fallback_size, True, custom_stem_count

    if not size_id:
        raise ValueError('Please select a bouquet size.')

    size = BouquetSize.objects.get(id=size_id)
    if total_stems < size.flower_count_min or total_stems > size.flower_count_max:
        raise ValueError(
            f'{size.get_size_display()} requires {size.flower_count_min}-{size.flower_count_max} flowers, '
            f'but you selected {total_stems}.'
        )

    return size, False, None


def bouquet_builder(request):
    """Main bouquet builder page."""
    sizes = BouquetSize.objects.all()
    wrapping_styles = WrappingStyle.objects.all()
    ribbon_colors = RibbonColor.objects.all()
    default_ribbon = ribbon_colors.first()
    extras = Extra.objects.all()
    flowers = Flower.objects.filter(availability_status='IN_STOCK')
    
    context = {
        'sizes': sizes,
        'wrapping_styles': wrapping_styles,
        'ribbon_colors': ribbon_colors,
        'default_ribbon': default_ribbon,
        'extras': extras,
        'flowers': flowers,
    }
    return render(request, 'custom_bouquet/builder.html', context)


def get_bouquet_pricing(request):
    """Calculate bouquet pricing (AJAX)."""
    try:
        size_id = request.GET.get('size_id')
        custom_stem_count_raw = request.GET.get('custom_stem_count')
        wrapping_id = request.GET.get('wrapping_id')
        ribbon_id = request.GET.get('ribbon_id')
        flower_ids = [flower_id for flower_id in request.GET.getlist('flower_ids') if flower_id]
        flower_quantities = request.GET.getlist('flower_quantities')
        extra_ids = [extra_id for extra_id in request.GET.getlist('extra_ids') if extra_id]
        extra_quantities = request.GET.getlist('extra_quantities')

        wrapping = WrappingStyle.objects.get(id=wrapping_id) if wrapping_id else WrappingStyle.objects.first()
        ribbon = RibbonColor.objects.get(id=ribbon_id) if ribbon_id else RibbonColor.objects.first()

        flowers_price = 0
        total_stems = 0
        flower_breakdown = []
        for index, flower_id in enumerate(flower_ids):
            flower = Flower.objects.get(id=flower_id)
            quantity = int(flower_quantities[index]) if index < len(flower_quantities) else 1
            subtotal = float(flower.price) * quantity
            flowers_price += subtotal
            total_stems += quantity
            flower_breakdown.append({
                'id': flower.id,
                'name': flower.get_name_display(),
                'quantity': quantity,
                'subtotal': subtotal,
            })

        extras_price = 0
        extras_breakdown = []
        for index, extra_id in enumerate(extra_ids):
            extra = Extra.objects.get(id=extra_id)
            quantity = int(extra_quantities[index]) if index < len(extra_quantities) else 1
            subtotal = float(extra.price) * quantity
            extras_price += subtotal
            extras_breakdown.append({
                'id': extra.id,
                'name': extra.get_name_display(),
                'quantity': quantity,
                'subtotal': subtotal,
            })

        custom_stem_count = int(custom_stem_count_raw) if custom_stem_count_raw not in (None, '') else None
        size, is_custom_size, resolved_custom_count = _resolve_selected_size(size_id, total_stems, custom_stem_count)
        
        total = float(wrapping.price) + float(ribbon.price) + flowers_price + extras_price
        
        return JsonResponse({
            'success': True,
            'size_price': 0,
            'size_name': f'Custom ({resolved_custom_count} stems)' if is_custom_size and resolved_custom_count else size.get_size_display(),
            'wrapping_price': float(wrapping.price),
            'ribbon_price': float(ribbon.price),
            'flowers_price': flowers_price,
            'extras_price': extras_price,
            'total': total,
            'flower_breakdown': flower_breakdown,
            'extras_breakdown': extras_breakdown,
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
        custom_stem_count_raw = data.get('custom_stem_count')
        wrapping_id = data.get('wrapping_id')
        ribbon_id = data.get('ribbon_id')
        flowers_data = data.get('flowers', [])  # List of {'flower_id': ..., 'quantity': ...}
        extras_data = data.get('extras', [])
        personal_message = data.get('personal_message', '')
        florist_instructions = data.get('florist_instructions', '')
        
        wrapping = WrappingStyle.objects.get(id=wrapping_id) if wrapping_id else WrappingStyle.objects.first()
        ribbon = RibbonColor.objects.get(id=ribbon_id) if ribbon_id else RibbonColor.objects.first()

        if not wrapping or not ribbon:
            raise ValueError('Bouquet configuration is incomplete. Please configure wrapping defaults in admin.')
        
        # Calculate total price
        flowers_price = 0
        extras_price = 0
        total_stems = 0

        for flower_data in flowers_data:
            quantity = int(flower_data.get('quantity', 1))
            total_stems += quantity

        custom_stem_count = int(custom_stem_count_raw) if custom_stem_count_raw not in (None, '') else None
        size, is_custom_size, resolved_custom_count = _resolve_selected_size(size_id, total_stems, custom_stem_count)
        
        bouquet = Bouquet.objects.create(
            name=name,
            description=florist_instructions,
            size=size,
            is_custom_size=is_custom_size,
            custom_flower_count=resolved_custom_count,
            wrapping=wrapping,
            ribbon_color=ribbon,
            personal_message=personal_message,
            base_price=0,
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
        total = float(wrapping.price) + float(ribbon.price) + flowers_price + extras_price
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
