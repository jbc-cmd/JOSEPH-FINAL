from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile, DeliveryAddress
from orders.models import Order


def register(request):
    """User registration."""
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        phone_number = request.POST.get('phone_number', '')
        
        # Validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return redirect('accounts:register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('accounts:register')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered')
            return redirect('accounts:register')
        
        # Create user
        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )
            
            # Update profile
            user.profile.phone_number = phone_number
            user.profile.save()
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return redirect('accounts:register')
    
    return render(request, 'accounts/register.html')


def login_view(request):
    """User login."""
    if request.user.is_authenticated:
        return redirect('products:home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'products:home')
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout."""
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('products:home')


@login_required(login_url='accounts:login')
def profile(request):
    """User profile page."""
    user_profile = request.user.profile
    addresses = request.user.delivery_addresses.all()
    recent_orders = request.user.orders.all()[:5]
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        user_profile.phone_number = phone_number
        user_profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:profile')
    
    context = {
        'profile': user_profile,
        'addresses': addresses,
        'recent_orders': recent_orders,
    }
    return render(request, 'accounts/profile.html', context)


@login_required(login_url='accounts:login')
def order_history(request):
    """View user's order history."""
    orders = request.user.orders.all()
    
    context = {'orders': orders}
    return render(request, 'accounts/order_history.html', context)


class DeliveryAddressCreateView(LoginRequiredMixin, CreateView):
    """Add new delivery address."""
    model = DeliveryAddress
    fields = ['label', 'recipient_name', 'phone_number', 'address', 'city', 'postal_code', 'notes', 'is_default']
    template_name = 'accounts/add_address.html'
    success_url = reverse_lazy('accounts:profile')
    login_url = 'accounts:login'
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)
    
    def get_success_url(self):
        messages.success(self.request, 'Address added successfully!')
        return reverse_lazy('accounts:profile')


class DeliveryAddressUpdateView(LoginRequiredMixin, UpdateView):
    """Edit delivery address."""
    model = DeliveryAddress
    fields = ['label', 'recipient_name', 'phone_number', 'address', 'city', 'postal_code', 'notes', 'is_default']
    template_name = 'accounts/edit_address.html'
    success_url = reverse_lazy('accounts:profile')
    login_url = 'accounts:login'
    
    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        messages.success(self.request, 'Address updated successfully!')
        return reverse_lazy('accounts:profile')


class DeliveryAddressDeleteView(LoginRequiredMixin, DeleteView):
    """Delete delivery address."""
    model = DeliveryAddress
    template_name = 'accounts/delete_address.html'
    success_url = reverse_lazy('accounts:profile')
    login_url = 'accounts:login'
    
    def get_queryset(self):
        return DeliveryAddress.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Address deleted successfully!')
        return super().delete(request, *args, **kwargs)
