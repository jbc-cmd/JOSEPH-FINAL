import json

from django.contrib import messages
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from orders.models import Order
from .models import Payment
from .services import PayMongoError, retrieve_checkout_session, verify_webhook_signature

PAYMONGO_REDIRECT_METHODS = {'GCASH'}


def _mark_payment_completed(payment, *, reference_number='', checkout_session_id=''):
    payment.status = 'COMPLETED'
    payment.payment_gateway = 'PAYMONGO'
    if reference_number:
        payment.reference_number = reference_number[:100]
    if checkout_session_id:
        payment.transaction_id = checkout_session_id[:255]
    if payment.paid_at is None:
        payment.paid_at = timezone.now()
    payment.save(update_fields=['status', 'payment_gateway', 'reference_number', 'transaction_id', 'paid_at', 'updated_at'])


def _mark_payment_failed(payment, *, reference_number=''):
    payment.status = 'FAILED'
    payment.payment_gateway = 'PAYMONGO'
    if reference_number:
        payment.reference_number = reference_number[:100]
    payment.save(update_fields=['status', 'payment_gateway', 'reference_number', 'updated_at'])


def _extract_session_payment_reference(session_payload):
    attributes = session_payload.get('data', {}).get('attributes', {})
    payments = attributes.get('payments') or []
    if not payments:
        return ''
    payment_id = payments[0].get('id', '')
    return payment_id


def _session_has_paid_payment(session_payload):
    attributes = session_payload.get('data', {}).get('attributes', {})
    payments = attributes.get('payments') or []
    for item in payments:
        payment_attributes = item.get('attributes') or {}
        if (payment_attributes.get('status') or '').lower() == 'paid':
            return True
    return False


@require_GET
def paymongo_return(request):
    order = get_object_or_404(Order, id=request.GET.get('order_id'))
    payment = getattr(order, 'payment', None)
    status = request.GET.get('status', '').lower()

    if not payment or payment.payment_method not in PAYMONGO_REDIRECT_METHODS:
        return redirect('orders:order_confirmation', order_id=order.id)

    if payment.status != 'COMPLETED' and payment.transaction_id:
        try:
            session_payload = retrieve_checkout_session(payment.transaction_id)
            reference_number = _extract_session_payment_reference(session_payload)

            if _session_has_paid_payment(session_payload):
                _mark_payment_completed(
                    payment,
                    reference_number=reference_number or order.order_number,
                    checkout_session_id=session_payload.get('data', {}).get('id', ''),
                )
            elif status == 'cancel':
                _mark_payment_failed(payment, reference_number=reference_number or order.order_number)
        except PayMongoError:
            if status == 'cancel':
                messages.warning(request, 'Your PayMongo checkout was cancelled before payment was completed.')
            else:
                messages.info(request, 'We are still waiting for payment confirmation from PayMongo. Please refresh this page in a moment.')
            return redirect('orders:order_detail', order_id=order.id)

    if payment.status == 'COMPLETED':
        messages.success(request, f'Your {payment.get_payment_method_display()} payment was confirmed successfully.')
        return redirect('orders:order_confirmation', order_id=order.id)

    if status == 'cancel':
        messages.warning(request, 'Your GCash checkout was cancelled before payment was completed.')
    else:
        messages.info(request, 'Your order was created. We are still waiting for final payment confirmation from PayMongo.')
    return redirect('orders:order_detail', order_id=order.id)


@csrf_exempt
@require_POST
def paymongo_webhook(request):
    signature_header = request.headers.get('Paymongo-Signature', '')
    if not verify_webhook_signature(signature_header=signature_header, raw_body=request.body):
        return HttpResponseBadRequest('Invalid PayMongo signature.')

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return HttpResponseBadRequest('Invalid payload.')

    event_attributes = payload.get('data', {}).get('attributes', {})
    event_type = event_attributes.get('type')
    if event_type != 'checkout_session.payment.paid':
        return JsonResponse({'message': 'IGNORED'}, status=200)

    session_data = event_attributes.get('data', {})
    checkout_session_id = session_data.get('id', '')
    session_attributes = session_data.get('attributes', {})
    metadata = session_attributes.get('metadata') or {}
    order_id = metadata.get('order_id')
    if not order_id:
        return JsonResponse({'message': 'MISSING_ORDER'}, status=200)

    order = get_object_or_404(Order, id=order_id)
    payment = getattr(order, 'payment', None)
    if not payment:
        return JsonResponse({'message': 'MISSING_PAYMENT'}, status=200)

    reference_number = _extract_session_payment_reference({'data': session_data}) or order.order_number
    _mark_payment_completed(
        payment,
        reference_number=reference_number,
        checkout_session_id=checkout_session_id,
    )
    return JsonResponse({'message': 'SUCCESS'}, status=200)
