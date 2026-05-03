from datetime import datetime, time, timedelta
from decimal import Decimal

from django.test import TestCase, override_settings
from django.utils import timezone

from delivery.models import DeliveryTimeWindow
from orders.models import Order

from .services import get_sales_chart_data


@override_settings(TIME_ZONE='Asia/Manila')
class SalesChartDataTests(TestCase):
    def setUp(self):
        self.delivery_window = DeliveryTimeWindow.objects.create(
            window='MORNING',
            start_time=time(8, 0),
            end_time=time(13, 0),
        )

    def create_order(self, day, total, payment_status='COMPLETED'):
        order = Order.objects.create(
            customer_name='Chart Customer',
            customer_email='chart@example.com',
            customer_phone='09171234567',
            delivery_address='123 Flower Street',
            delivery_city='Manila',
            delivery_postal_code='1000',
            delivery_date=day,
            delivery_time_window=self.delivery_window,
            payment_status=payment_status,
            subtotal=Decimal(total),
            delivery_fee=Decimal('0.00'),
            total_amount=Decimal(total),
        )
        created_at = timezone.make_aware(datetime.combine(day, time(10, 0)))
        Order.objects.filter(pk=order.pk).update(created_at=created_at)
        return order

    def test_sales_chart_returns_real_seven_day_calendar_series(self):
        today = timezone.localdate()
        expected_dates = [today - timedelta(days=offset) for offset in range(6, -1, -1)]

        self.create_order(today - timedelta(days=2), '300.00')
        self.create_order(today - timedelta(days=1), '999.00', payment_status='PENDING')
        self.create_order(today, '500.00')

        data = get_sales_chart_data()

        self.assertEqual(len(data), 7)
        self.assertEqual([item['date'] for item in data], [day.isoformat() for day in expected_dates])
        self.assertEqual([item['label'] for item in data], [day.strftime('%a') for day in expected_dates])
        self.assertEqual(data[-3]['sales'], 300.0)
        self.assertEqual(data[-3]['orders'], 1)
        self.assertEqual(data[-2]['sales'], 0.0)
        self.assertEqual(data[-2]['orders'], 0)
        self.assertEqual(data[-1]['sales'], 500.0)
        self.assertEqual(data[-1]['orders'], 1)
