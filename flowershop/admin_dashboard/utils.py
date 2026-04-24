from functools import wraps

from decimal import Decimal
from io import BytesIO

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse

from .models import AdminActivityLog, AdminSetting


def is_admin_user(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = f"{reverse('accounts:login')}?next={request.get_full_path()}"
            return HttpResponseRedirect(login_url)
        if not is_admin_user(request.user):
            return admin_redirect_response(request)
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def admin_redirect_response(request):
    messages.error(request, 'You do not have permission to access the admin dashboard.')
    return redirect('products:home')


class AdminRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            login_url = f"{reverse('accounts:login')}?next={request.get_full_path()}"
            return HttpResponseRedirect(login_url)
        if not is_admin_user(request.user):
            return admin_redirect_response(request)
        return super().dispatch(request, *args, **kwargs)


def get_client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def get_admin_settings():
    settings_obj, _ = AdminSetting.objects.get_or_create(pk=1)
    return settings_obj


def log_admin_activity(
    request,
    *,
    category,
    action,
    description='',
    target_type='',
    target_id='',
    target_label='',
    metadata=None,
):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return

    AdminActivityLog.objects.create(
        admin_user=request.user,
        category=category,
        action=action,
        description=description,
        target_type=target_type,
        target_id=str(target_id or ''),
        target_label=target_label,
        ip_address=get_client_ip(request),
        metadata=metadata or {},
    )


def money(value):
    return Decimal(value or 0)


def build_simple_pdf(title, lines):
    buffer = BytesIO()
    content_stream = [
        'BT',
        '/F1 12 Tf',
        '50 780 Td',
        f'({escape_pdf_text(title)}) Tj',
    ]
    y_offset = 760
    for line in lines:
        content_stream.extend([
            'BT',
            '/F1 10 Tf',
            f'50 {y_offset} Td',
            f'({escape_pdf_text(line[:110])}) Tj',
            'ET',
        ])
        y_offset -= 16
        if y_offset <= 40:
            break

    stream = '\n'.join(content_stream).encode('latin-1', errors='replace')
    objects = []
    objects.append(b'1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n')
    objects.append(b'2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n')
    objects.append(b'3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n')
    objects.append(b'4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n')
    objects.append(f'5 0 obj << /Length {len(stream)} >> stream\n'.encode('latin-1') + stream + b'\nendstream endobj\n')

    buffer.write(b'%PDF-1.4\n')
    offsets = [0]
    for obj in objects:
        offsets.append(buffer.tell())
        buffer.write(obj)
    xref_pos = buffer.tell()
    buffer.write(f'xref\n0 {len(offsets)}\n'.encode('latin-1'))
    buffer.write(b'0000000000 65535 f \n')
    for offset in offsets[1:]:
        buffer.write(f'{offset:010d} 00000 n \n'.encode('latin-1'))
    buffer.write(
        f'trailer << /Size {len(offsets)} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF'.encode('latin-1')
    )
    return buffer.getvalue()


def escape_pdf_text(value):
    return (
        str(value)
        .replace('\\', '\\\\')
        .replace('(', '\\(')
        .replace(')', '\\)')
    )
