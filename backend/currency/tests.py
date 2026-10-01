from django.test import TestCase

from crm.models import ClientProfile
from currency.models import Orders


class OrdersClientRelationTest(TestCase):
    def test_order_creates_and_links_client_profile(self):
        order = Orders.objects.create(
            clients_telephone='+380991234567',
            address_exchanger='ул. Пример, 12',
            currency_name='USD',
            buy_or_sell='Купить',
            exchange_rate='27.50',
            order_sum=100,
        )

        self.assertIsNotNone(order.client)
        self.assertEqual(order.client.phone, '+380991234567')
        self.assertIn(order, order.client.orders.all())
