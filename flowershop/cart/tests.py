from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from products.models import Product

from .models import Cart, CartItem


class CartRemovalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cart-user', password='pass')
        self.other_user = User.objects.create_user(username='other-cart-user', password='pass')
        self.product = Product.objects.create(
            name='Test Bouquet',
            description='A test bouquet',
            price='500.00',
            stock_quantity=10,
        )
        self.cart = Cart.objects.create(user=self.user)
        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=1,
            price_at_purchase=self.product.price,
        )
        self.other_cart = Cart.objects.create(user=self.other_user)
        self.other_cart_item = CartItem.objects.create(
            cart=self.other_cart,
            product=self.product,
            quantity=1,
            price_at_purchase=self.product.price,
        )

    def test_cart_page_remove_control_posts_to_remove_view(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse('cart:cart'))

        self.assertContains(response, 'method="post"')
        self.assertContains(response, f'action="{reverse("cart:remove_from_cart", args=[self.cart_item.id])}"')

    def test_post_remove_deletes_item_from_current_cart(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('cart:remove_from_cart', args=[self.cart_item.id]),
            {'next': reverse('cart:cart')},
        )

        self.assertRedirects(response, reverse('cart:cart'))
        self.assertFalse(CartItem.objects.filter(id=self.cart_item.id).exists())
        self.assertTrue(CartItem.objects.filter(id=self.other_cart_item.id).exists())

    def test_user_cannot_remove_item_from_another_cart(self):
        self.client.force_login(self.user)

        response = self.client.post(reverse('cart:remove_from_cart', args=[self.other_cart_item.id]))

        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(id=self.other_cart_item.id).exists())
