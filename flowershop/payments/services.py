import hashlib
import hmac
from decimal import Decimal, InvalidOperation

import requests
from django.conf import settings


PAYMONGO_API_BASE = 'https://api.paymongo.com/v1'


class PayMongoError(Exception):
    """Raised when the PayMongo API returns an actionable error."""


def paymongo_is_configured():
    return bool(getattr(settings, 'PAYMONGO_SECRET_KEY', ''))


def _auth():
    secret_key = getattr(settings, 'PAYMONGO_SECRET_KEY', '')
    if not secret_key:
        raise PayMongoError('PayMongo is not configured yet. Add your PayMongo secret key first.')
    return (secret_key, '')


def _extract_error_message(response):
    try:
        payload = response.json()
    except ValueError:
        return f'PayMongo request failed with status {response.status_code}.'

    errors = payload.get('errors') or []
    if errors:
        first_error = errors[0]
        detail = first_error.get('detail') or first_error.get('code')
        if detail:
            return detail

    return f'PayMongo request failed with status {response.status_code}.'


def _request(method, path, *, json=None):
    response = requests.request(
        method,
        f'{PAYMONGO_API_BASE}{path}',
        auth=_auth(),
        json=json,
        timeout=30,
    )
    if response.status_code >= 400:
        raise PayMongoError(_extract_error_message(response))
    return response.json()


def amount_to_centavos(value):
    try:
        amount = Decimal(value)
    except (InvalidOperation, TypeError):
        raise PayMongoError('Invalid amount supplied to PayMongo.')
    return int((amount * Decimal('100')).quantize(Decimal('1')))


def build_paymongo_line_items(order):
    line_items = []
    for item in order.items.all():
        line_items.append({
            'currency': 'PHP',
            'amount': amount_to_centavos(item.price),
            'name': item.get_item_name(),
            'quantity': item.quantity,
        })

    if order.delivery_fee:
        line_items.append({
            'currency': 'PHP',
            'amount': amount_to_centavos(order.delivery_fee),
            'name': 'Delivery Fee',
            'quantity': 1,
        })

    return line_items


def create_checkout_session(*, order, request, payment_method_types):
    success_url = request.build_absolute_uri(f"/payments/paymongo/return/?order_id={order.id}&status=success")
    cancel_url = request.build_absolute_uri(f"/payments/paymongo/return/?order_id={order.id}&status=cancel")

    payload = {
        'data': {
            'attributes': {
                'billing': {
                    'name': order.customer_name,
                    'email': order.customer_email,
                    'phone': order.customer_phone,
                },
                'cancel_url': cancel_url,
                'description': f'Joseph Flowershop order {order.order_number}',
                'line_items': build_paymongo_line_items(order),
                'payment_method_types': payment_method_types,
                'reference_number': order.order_number,
                'send_email_receipt': True,
                'show_description': True,
                'show_line_items': True,
                'success_url': success_url,
                'metadata': {
                    'order_id': str(order.id),
                    'order_number': order.order_number,
                },
            }
        }
    }

    return _request('POST', '/checkout_sessions', json=payload)


def retrieve_checkout_session(checkout_session_id):
    return _request('GET', f'/checkout_sessions/{checkout_session_id}')


def verify_webhook_signature(*, signature_header, raw_body):
    secret = getattr(settings, 'PAYMONGO_WEBHOOK_SECRET', '')
    if not secret or not signature_header:
        return False

    parts = {}
    for part in signature_header.split(','):
        key, _, value = part.partition('=')
        parts[key.strip()] = value.strip()

    timestamp = parts.get('t')
    if not timestamp:
        return False

    signed_payload = f'{timestamp}.{raw_body.decode("utf-8")}'.encode('utf-8')
    expected = hmac.new(secret.encode('utf-8'), signed_payload, hashlib.sha256).hexdigest()

    provided = parts.get('li') or parts.get('te')
    if not provided:
        return False

    return hmac.compare_digest(expected, provided)
