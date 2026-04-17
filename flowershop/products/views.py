from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import Product, Category, Flower, ProductReview
from django.core.paginator import Paginator
import requests


class HomeView(ListView):
    """Home page with featured products."""
    model = Product
    template_name = 'products/home.html'
    context_object_name = 'featured_products'
    paginate_by = 12
    
    def get_queryset(self):
        return Product.objects.filter(is_featured=True, is_available=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['all_flowers'] = Flower.objects.filter(availability_status='IN_STOCK')
        return context


class AboutView(TemplateView):
    """About page."""
    template_name = 'products/about.html'


class ContactView(TemplateView):
    """Contact page."""
    template_name = 'products/contact.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault('form_data', {
            'name': '',
            'email': '',
            'subject': '',
            'message': '',
        })
        return context

    def post(self, request, *args, **kwargs):
        form_data = {
            'name': request.POST.get('name', '').strip(),
            'email': request.POST.get('email', '').strip(),
            'subject': request.POST.get('subject', '').strip(),
            'message': request.POST.get('message', '').strip(),
        }

        if not all(form_data.values()):
            messages.error(request, 'Please fill out all fields before sending.')
            return self.render_to_response(self.get_context_data(form_data=form_data))

        full_message = f"Name: {form_data['name']}\nEmail: {form_data['email']}\n\n{form_data['message']}"
        try:
            if getattr(settings, 'RESEND_API_KEY', ''):
                response = requests.post(
                    'https://api.resend.com/emails',
                    headers={
                        'Authorization': f"Bearer {settings.RESEND_API_KEY}",
                        'Content-Type': 'application/json',
                        'User-Agent': 'joseph-flowershop/1.0',
                    },
                    json={
                        'from': settings.CONTACT_FROM_EMAIL,
                        'to': [settings.CONTACT_TO_EMAIL],
                        'subject': form_data['subject'],
                        'text': full_message,
                        'reply_to': form_data['email'],
                    },
                    timeout=15,
                )
                response.raise_for_status()
            else:
                send_mail(
                    form_data['subject'],
                    full_message,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.DEFAULT_FROM_EMAIL],
                    fail_silently=False,
                )
        except Exception:
            messages.error(request, 'We could not send your message right now. Please try again later or contact us directly.')
            return self.render_to_response(self.get_context_data(form_data=form_data))

        messages.success(request, 'Thanks! Your message has been sent.')
        return redirect('products:contact')


class TermsView(TemplateView):
    """Terms of service page."""
    template_name = 'products/terms.html'


class PrivacyView(TemplateView):
    """Privacy policy page."""
    template_name = 'products/privacy.html'


class ShopView(ListView):
    """Shop page with all products and filtering."""
    model = Product
    template_name = 'products/shop.html'
    context_object_name = 'products'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_available=True)
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by size
        size = self.request.GET.get('size')
        if size:
            queryset = queryset.filter(size=size)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        # Sort
        sort_by = self.request.GET.get('sort', '-created_at')
        if sort_by in ['name', '-name', 'price', '-price', 'rating', '-rating']:
            queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['selected_category'] = self.request.GET.get('category', '')
        context['search_query'] = self.request.GET.get('search', '')
        context['sort_by'] = self.request.GET.get('sort', '-created_at')
        return context


class ProductDetailView(DetailView):
    """Product detail page."""
    model = Product
    template_name = 'products/product_detail.html'
    context_object_name = 'product'
    slug_field = 'slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        product = self.get_object()
        context['reviews'] = product.reviews.filter(is_approved=True).order_by('-created_at')
        context['average_rating'] = product.rating
        context['user_review'] = product.reviews.filter(user=self.request.user).first() if self.request.user.is_authenticated else None
        context['related_products'] = Product.objects.filter(
            category=product.category,
            is_available=True
        ).exclude(id=product.id)[:4]
        return context


@login_required(login_url='accounts:login')
def submit_review(request, slug):
    """Submit or update a product review."""
    product = get_object_or_404(Product, slug=slug, is_available=True)

    if request.method != 'POST':
        return redirect('products:product_detail', slug=slug)

    rating = request.POST.get('rating', '').strip()
    comment = request.POST.get('comment', '').strip()
    photo = request.FILES.get('photo')

    if not rating or rating not in {'1', '2', '3', '4', '5'}:
        messages.error(request, 'Please choose a star rating from 1 to 5.')
        return redirect('products:product_detail', slug=slug)

    if not comment:
        messages.error(request, 'Please write a short review before submitting.')
        return redirect('products:product_detail', slug=slug)

    existing_review = product.reviews.filter(user=request.user).first()
    has_purchased_product = request.user.orders.filter(items__product=product).exists()
    review_defaults = {
        'customer_name': request.user.get_full_name() or request.user.username,
        'customer_email': request.user.email,
        'rating': int(rating),
        'comment': comment,
        'photo': photo if photo else (existing_review.photo if existing_review else None),
        'is_verified_purchase': has_purchased_product or (existing_review.is_verified_purchase if existing_review else False),
        'is_approved': existing_review.is_approved if existing_review else False,
    }

    if existing_review:
        for field, value in review_defaults.items():
            setattr(existing_review, field, value)
        if photo is None and 'remove_photo' in request.POST:
            existing_review.photo = None
        existing_review.is_approved = False
        existing_review.save()
        product.update_review_stats()
        messages.success(request, 'Your review was updated and is awaiting approval.')
    else:
        ProductReview.objects.create(
            product=product,
            user=request.user,
            **review_defaults,
        )
        product.update_review_stats()
        messages.success(request, 'Thanks for your review. It is now awaiting approval.')

    return redirect('products:product_detail', slug=slug)


def quick_view(request, slug):
    """AJAX quick view for products."""
    product = get_object_or_404(Product, slug=slug)
    return JsonResponse({
        'id': product.id,
        'name': product.name,
        'price': str(product.price),
        'image': product.image.url if product.image else '',
        'description': product.description[:200],
        'rating': product.rating,
    })


def search_products(request):
    """Search products API."""
    query = request.GET.get('q', '')
    products = Product.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query),
        is_available=True
    )[:10]

    results = [{
        'id': p.id,
        'name': p.name,
        'slug': p.slug,
        'image': p.image.url if p.image else '',
        'price': str(p.price),
    } for p in products]

    return JsonResponse({'results': results})
