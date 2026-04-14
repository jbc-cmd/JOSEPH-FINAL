import base64
import re
import uuid

from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.models import User
from django.views.generic import CreateView, ListView, DetailView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import UserProfile, DeliveryAddress
from orders.models import Order


def _avatar_extension_from_header(header):
    mime_type = header.split(':', 1)[1].split(';', 1)[0].strip().lower()
    extension_map = {
        'image/jpeg': 'jpg',
        'image/jpg': 'jpg',
        'image/png': 'png',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'image/svg+xml': 'svg',
    }
    return extension_map.get(mime_type)


NAME_PATTERN = re.compile(r"^[A-Za-z]+(?:[ -][A-Za-z]+)*$")
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.]{4,30}$")
PHONE_SANITIZE_PATTERN = re.compile(r"[\s\-()]")
PHONE_PATTERN = re.compile(r"^\+?\d{10,15}$")
RESERVED_USERNAMES = {
    'admin', 'administrator', 'root', 'system', 'support', 'help',
    'owner', 'staff', 'null', 'none', 'me', 'account', 'login', 'signup',
}


def _normalize_name(value):
    return re.sub(r"\s+", " ", value.strip())


def _normalize_phone_number(value):
    return PHONE_SANITIZE_PATTERN.sub('', value.strip())


def _build_register_context(form_data=None, errors=None, next_url=''):
    return {
        'form_data': form_data or {},
        'register_errors': errors or {},
        'next_url': next_url,
    }


def register(request):
    """User registration."""
    if request.method == 'POST':
        next_url = request.POST.get('next') or request.GET.get('next', '')
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip().lower()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        first_name = _normalize_name(request.POST.get('first_name', ''))
        last_name = _normalize_name(request.POST.get('last_name', ''))
        raw_phone_number = request.POST.get('phone_number', '').strip()
        phone_number = _normalize_phone_number(raw_phone_number)
        agreed_to_terms = request.POST.get('agree') == 'on'

        form_data = {
            'username': username,
            'email': email,
            'first_name': first_name,
            'last_name': last_name,
            'phone_number': raw_phone_number,
            'agree': agreed_to_terms,
        }
        errors = {}

        if not first_name:
            errors['first_name'] = 'First name is required.'
        elif not 2 <= len(first_name) <= 50:
            errors['first_name'] = 'First name must be between 2 and 50 characters.'
        elif not NAME_PATTERN.fullmatch(first_name):
            errors['first_name'] = 'First name can only contain letters, spaces, and hyphens.'

        if not last_name:
            errors['last_name'] = 'Last name is required.'
        elif not 2 <= len(last_name) <= 50:
            errors['last_name'] = 'Last name must be between 2 and 50 characters.'
        elif not NAME_PATTERN.fullmatch(last_name):
            errors['last_name'] = 'Last name can only contain letters, spaces, and hyphens.'

        if not username:
            errors['username'] = 'Username is required.'
        elif username.lower() in RESERVED_USERNAMES:
            errors['username'] = 'Please choose a different username.'
        elif not USERNAME_PATTERN.fullmatch(username):
            errors['username'] = 'Username must be 4-30 characters and use only letters, numbers, underscores, or dots.'
        elif username.startswith('.') or username.endswith('.') or '..' in username:
            errors['username'] = 'Username format is not allowed.'
        elif User.objects.filter(username__iexact=username).exists():
            errors['username'] = 'This username is already in use.'

        if not email:
            errors['email'] = 'Email is required.'
        else:
            try:
                validate_email(email)
            except ValidationError:
                errors['email'] = 'Enter a valid email address.'
            else:
                if User.objects.filter(email__iexact=email).exists():
                    errors['email'] = 'This email is already in use.'

        if not phone_number:
            errors['phone_number'] = 'Phone number is required.'
        elif not PHONE_PATTERN.fullmatch(phone_number):
            errors['phone_number'] = 'Enter a valid phone number using 10 to 15 digits.'

        if not password1:
            errors['password1'] = 'Password is required.'
        elif len(password1) < 8:
            errors['password1'] = 'Password must be at least 8 characters.'
        elif not re.search(r'[A-Z]', password1):
            errors['password1'] = 'Password must include at least one uppercase letter.'
        elif not re.search(r'[a-z]', password1):
            errors['password1'] = 'Password must include at least one lowercase letter.'
        elif not re.search(r'\d', password1):
            errors['password1'] = 'Password must include at least one number.'
        elif not re.search(r'[^A-Za-z0-9]', password1):
            errors['password1'] = 'Password must include at least one special character.'

        if not password2:
            errors['password2'] = 'Please confirm your password.'
        elif password1 != password2:
            errors['password2'] = 'Passwords do not match.'

        if not agreed_to_terms:
            errors['agree'] = 'You must agree to the Terms of Service and Privacy Policy.'

        if password1 and 'password1' not in errors:
            temp_user = User(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            try:
                validate_password(password1, user=temp_user)
            except ValidationError as exc:
                errors['password1'] = exc.messages[0]

        if errors:
            return render(request, 'accounts/register.html', _build_register_context(form_data, errors, next_url))

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name
            )

            user_profile, _ = UserProfile.objects.get_or_create(user=user)
            user_profile.phone_number = phone_number
            user_profile.full_clean()
            user_profile.save()

            login(request, user)

            storage = messages.get_messages(request)
            storage.used = True

            if next_url and 'checkout' in next_url:
                messages.success(request, '✓ Account created and logged in! Returning to checkout...')
                return redirect(next_url)
            else:
                messages.success(request, '✓ Account created successfully! Welcome aboard!')
                return redirect('products:home')

        except ValidationError as exc:
            errors['phone_number'] = exc.messages[0]
            return render(request, 'accounts/register.html', _build_register_context(form_data, errors, next_url))
        except Exception:
            messages.error(request, 'We could not create your account right now. Please try again.')
            return render(request, 'accounts/register.html', _build_register_context(form_data, {}, next_url))

    return render(request, 'accounts/register.html', _build_register_context(next_url=request.GET.get('next', '')))


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
            action = request.GET.get('action', '')

            # Clear all existing messages
            storage = messages.get_messages(request)
            storage.used = True

            # Show different message based on context
            if 'checkout' in next_url:
                messages.success(request, '✓ You\'ve been logged in! Returning to checkout...')
            elif action == 'add_to_cart':
                messages.success(request, '✓ You\'ve been logged in! Your item has been added to cart.')
                # Redirect to apply pending cart item
                return redirect('cart:apply_pending')
            else:
                messages.success(request, f'Welcome back, {user.first_name or user.username}!')

            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """User logout."""
    logout(request)

    # Clear all existing messages
    storage = messages.get_messages(request)
    storage.used = True

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
        profile_picture = request.FILES.get('profile_picture')
        avatar_choice = request.POST.get('avatar_choice', '').strip()
        
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.email = email
        request.user.save()
        
        user_profile.phone_number = phone_number
        if profile_picture:
            user_profile.profile_picture = profile_picture
        elif avatar_choice.startswith('data:image/'):
            try:
                header, encoded = avatar_choice.split(',', 1)
                extension = _avatar_extension_from_header(header)
                if not extension:
                    raise ValueError('Unsupported avatar image type.')
                user_profile.profile_picture.save(
                    f'avatar_{request.user.id}_{uuid.uuid4().hex[:8]}.{extension}',
                    ContentFile(base64.b64decode(encoded)),
                    save=False,
                )
            except (ValueError, IndexError, base64.binascii.Error):
                messages.error(request, 'Selected avatar could not be applied.')
                return redirect('accounts:profile')
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
    
    def form_valid(self, form):
        messages.success(self.request, 'Address deleted successfully!')
        return super().form_valid(form)
