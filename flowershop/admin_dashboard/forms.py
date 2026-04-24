import secrets
import string

from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

from accounts.models import UserProfile
from configurations.models import GeneralConfig, ServiceConfig
from orders.models import Order
from payments.models import RefundRequest
from products.models import Category, Product

from .models import AdminSetting


class ProductAdminForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'name', 'slug', 'description', 'composition', 'product_type', 'category',
            'price', 'image', 'stock_quantity', 'size', 'is_featured', 'is_available',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'composition': forms.Textarea(attrs={'rows': 4}),
        }


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'description', 'image', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'payment_status']


class RefundStatusForm(forms.ModelForm):
    class Meta:
        model = RefundRequest
        fields = ['status', 'admin_notes', 'rejected_reason']
        widgets = {
            'admin_notes': forms.Textarea(attrs={'rows': 3}),
            'rejected_reason': forms.Textarea(attrs={'rows': 3}),
        }


class GeneralConfigForm(forms.ModelForm):
    class Meta:
        model = GeneralConfig
        fields = [
            'shop_name', 'shop_phone', 'shop_email', 'shop_address',
            'facebook_url', 'instagram_url', 'delivery_fee', 'min_order_amount',
        ]
        widgets = {
            'shop_address': forms.Textarea(attrs={'rows': 3}),
        }


class ServiceConfigForm(forms.ModelForm):
    class Meta:
        model = ServiceConfig
        fields = ['service_name', 'api_key', 'api_secret', 'environment', 'is_active']
        widgets = {
            'api_key': forms.PasswordInput(render_value=True),
            'api_secret': forms.PasswordInput(render_value=True),
        }


class AdminSettingForm(forms.ModelForm):
    class Meta:
        model = AdminSetting
        fields = [
            'site_title', 'support_email', 'tax_rate', 'currency_symbol',
            'low_stock_threshold', 'session_timeout_minutes', 'notify_new_orders',
            'notify_new_signups', 'notify_low_stock',
        ]


class AdminProfileForm(forms.ModelForm):
    first_name = forms.CharField(max_length=150)
    last_name = forms.CharField(max_length=150)
    email = forms.EmailField()

    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address', 'default_delivery_address', 'profile_picture']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'default_delivery_address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['first_name'].initial = user.first_name
        self.fields['last_name'].initial = user.last_name
        self.fields['email'].initial = user.email


class UserStatusForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['is_active', 'is_staff']


class AdminResetPasswordForm(SetPasswordForm):
    auto_generate = forms.BooleanField(required=False, initial=False)

    def save(self, commit=True):
        if self.cleaned_data.get('auto_generate'):
            alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
            password = ''.join(secrets.choice(alphabet) for _ in range(14))
            self.user.set_password(password)
            self.generated_password = password
            if commit:
                self.user.save()
            return self.user

        self.generated_password = ''
        return super().save(commit=commit)


class AdminChangeOwnPasswordForm(PasswordChangeForm):
    pass
