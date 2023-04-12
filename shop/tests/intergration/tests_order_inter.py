from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

from unittest.mock import patch

from shop.models import Product, OrderedProduct, Category, Order

import os

os.environ['DJANGO_SETTINGS_MODULE'] = 'src.settings'

User = get_user_model()


class ModelTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='Pet',
                                                  email='petya@gmail.com',
                                                  first_name='Petya',
                                                  last_name='Petro',
                                                  password='petya12345')

        self.category1 = Category.objects.create(name='chocolate', slug='chocolate')
        self.category2 = Category.objects.create(name='biscuit', slug='biscuit')

        self.product1 = Product.objects.create(name='Nestle',
                                               price=3,
                                               stock=5,
                                               category=self.category1,
                                               image='media/00015718.n_1_190x190.png.jpg')

        self.product2 = Product.objects.create(name='Rikki',
                                               price=4.85,
                                               stock=5,
                                               category=self.category2,
                                               image='media/00031114.n_1_190x190.png.jpg')

        self.order_user = Order.objects.create(user=self.test_user,
                                               first_name='',
                                               last_name='',
                                               all_price=0,
                                               all_qtc=0,
                                               city='',
                                               address='',
                                               comment='',
                                               status=settings.STATUS_IN_PROGRESS)

        self.order_anonymous_user = Order.objects.create(user=None,
                                                         first_name='',
                                                         last_name='',
                                                         all_price=0,
                                                         all_qtc=0,
                                                         city='',
                                                         address='',
                                                         comment='',
                                                         status=settings.STATUS_IN_PROGRESS)

        self.cart1 = OrderedProduct.objects.create(product=self.product1,
                                                   order=self.order_user,
                                                   prod_num=3)

        self.cart2 = OrderedProduct.objects.create(product=self.product2,
                                                   order=self.order_anonymous_user,
                                                   prod_num=5)

    @patch('shop.views.order.is_working_hours')
    def test_order_product_not_authenticated_user(self, mock_is_working_hours):
        self.client.force_login(self.test_user)
        mock_is_working_hours.return_value = True

        url = reverse('order')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/order.html')

    @patch('shop.views.order.messages')
    @patch('shop.views.order.is_working_hours')
    def test_order_product_not_working_hours(self, mock_is_working_hours, mock_messages):
        self.client.force_login(self.test_user)
        mock_is_working_hours.return_value = False

        url = reverse('order')
        response = self.client.get(url)

        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, settings.SHOP_OPENING_HOURS)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')

    @patch('shop.views.order.is_working_hours')
    def test_order_product(self, mock_is_working_hours):
        self.client.force_login(self.test_user)
        mock_is_working_hours.return_value = True
        data_form = {
            'city': 'Minsk',
            'address': 'chapaeva, 5',
            'phone': '+375293002010',
            'order_date': '2009-02-26T03:00:00',
            'comment': 'it is good product'
        }

        url = reverse('order')
        response = self.client.post(url, data_form)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/order.html')

    @patch('shop.views.order.sending_a_letter_to_the_customer')
    def test_send_order_user(self, mock_sending_a_letter_to_the_customer):
        mock_sending_a_letter_to_the_customer.return_value = True
        self.client.force_login(self.test_user)
        form = {
            'city': 'Minsk',
            'address': 'chapaeva, 5',
            'phone': '+375293002010',
            'order_date': '2021-12-31 23:59:59',
            'comment': 'it is good product'}

        url = reverse('send')
        response = self.client.post(url, form)

        self.assertTrue(mock_sending_a_letter_to_the_customer.return_value)
        Order.objects.filter(id=self.order_user.id).update(first_name='Petya',
                                                           last_name='Petro',
                                                           phone='+375293002010',
                                                           all_price=9,
                                                           all_qtc=3,
                                                           city='Minsk',
                                                           address='chapaeva, 5',
                                                           comment='it is good product',
                                                           status=settings.STATUS_COMPLETED)
        self.assertEqual(self.test_user.orders.values_list('status', flat=True)[0], settings.STATUS_COMPLETED)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    @patch('shop.views.order.sending_a_letter_to_the_customer')
    def test_send_order_anonymous_user(self, mock_sending_a_letter_to_the_customer):
        mock_sending_a_letter_to_the_customer.return_value = True
        form = {
            'first_name': 'Anonym',
            'last_name': 'Anonyms',
            'email': 'anonym@gmail.com',
            'city': 'Minsk',
            'address': 'chapaeva, 5',
            'phone': '+375291000000',
            'order_date': '2021-12-31 23:59:59',
            'comment': 'OK'}

        url = reverse('send')
        response = self.client.post(url, form)

        self.assertTrue(mock_sending_a_letter_to_the_customer.return_value)
        Order.objects.filter(id=self.order_anonymous_user.id).update(first_name='Anonym',
                                                                     last_name='Anonyms',
                                                                     phone='+375291000000',
                                                                     all_price=24.25,
                                                                     all_qtc=5,
                                                                     city='Minsk',
                                                                     address='chapaeva, 5',
                                                                     comment='OK',
                                                                     status=settings.STATUS_COMPLETED)
        self.assertEqual(Order.objects.filter(id=self.order_anonymous_user.id).values_list('status', flat=True)[0], settings.STATUS_COMPLETED)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')
