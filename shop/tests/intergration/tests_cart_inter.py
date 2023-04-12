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

    @patch('shop.views.cart.messages')
    def test_add_cart_user(self, mock_messages):
        self.client.force_login(self.test_user)
        product_id = self.product2.id

        url = reverse('add_cart', args=(product_id, ))
        response = self.client.get(url)

        self.assertEqual(OrderedProduct.objects.filter(order=self.order_user).count(), 2)
        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, 'Product added to cart!')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    @patch('shop.views.cart.messages')
    def test_add_cart_user_create_order(self, mock_messages):
        user = User.objects.create_user(username='Goof',
                                        email='petya@gmail.com',
                                        first_name='Oleg',
                                        last_name='Vasual',
                                        password='petya12345')

        product_id = self.product2.id
        self.client.force_login(user)

        url = reverse('add_cart', args=(product_id,))
        response = self.client.get(url)

        new_order, _ = Order.objects.get_or_create(user=user, status=settings.STATUS_IN_PROGRESS)
        OrderedProduct.objects.get_or_create(product=self.product2, order=new_order)
        self.assertNotEqual(new_order.id, self.order_user.id)
        self.assertEqual(OrderedProduct.objects.filter(order=new_order).count(), 1)
        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, 'Product added to cart!')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    @patch('shop.views.cart.messages')
    def test_add_cart_not_authenticated_user(self, mock_messages):
        session = self.client.session
        session['data'] = {'order': None}
        session.save()
        product_id = self.product2.id

        url = reverse('add_cart', args=(product_id, ))
        response = self.client.post(url)

        new_order_anonymous_user = Order.objects.create(user=None,
                                                        first_name='',
                                                        last_name='',
                                                        all_price=0,
                                                        all_qtc=0,
                                                        city='',
                                                        address='',
                                                        comment='',
                                                        status=settings.STATUS_IN_PROGRESS)
        OrderedProduct.objects.create(product=self.product2,
                                      order=new_order_anonymous_user,
                                      prod_num=1)
        self.assertEqual(OrderedProduct.objects.filter(
            order=new_order_anonymous_user.id).count(), 1)
        self.assertEqual(new_order_anonymous_user.id, 3)
        self.assertNotEqual(new_order_anonymous_user.id, self.order_anonymous_user.id)
        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, 'Product added to cart!')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    def test_cart_view_not_authenticated_user(self):
        session = self.client.session
        session['data'] = {'order': self.order_anonymous_user.id}
        session.save()

        url = reverse('cart')
        response = self.client.get(url)

        self.assertEqual(OrderedProduct.objects.filter(order=self.order_anonymous_user).count(), 1)
        OrderedProduct.objects.create(product=self.product2, order=self.order_anonymous_user)
        self.assertEqual(OrderedProduct.objects.filter(order=self.order_anonymous_user).count(), 2)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/cart.html')

    def test_cart_view_user(self):
        self.client.force_login(self.test_user)

        url = reverse('cart')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/cart.html')
        self.assertEqual(OrderedProduct.objects.filter(order=self.order_user).count(), 1)
        OrderedProduct.objects.create(product=self.product2, order=self.order_user)
        self.assertEqual(OrderedProduct.objects.filter(order=self.order_user).count(), 2)

    def test_delete_cart_prod_user(self):
        self.client.force_login(self.test_user)
        pk = self.product1.id

        url = reverse('delete', args=(pk, ))
        response = self.client.post(url)

        self.assertEqual(OrderedProduct.objects.filter(product=pk, order=self.order_user).count(), 0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')

    def test_delete_all_cart_prod_user(self):
        self.client.force_login(self.test_user)

        url = reverse('delete_full_cart')
        response = self.client.post(url)

        self.assertEqual(OrderedProduct.objects.filter(order=self.order_user).count(), 0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')

    def test_delete_cart_prod_authenticated_user(self):
        session = self.client.session
        session['data'] = {'order': self.order_anonymous_user.id}
        session.save()
        pk = self.product2.id

        url = reverse('delete', args=(pk, ))
        response = self.client.post(url)

        self.assertEqual(OrderedProduct.objects.filter(product=pk, order=self.order_anonymous_user.id).count(), 0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')

    def test_delete_all_cart_prod_authenticated_user(self):
        session = self.client.session
        session['data'] = {'order': self.order_anonymous_user.id}
        session.save()

        url = reverse('delete_full_cart')
        response = self.client.post(url)

        self.assertEqual(OrderedProduct.objects.filter(order=self.order_anonymous_user.id).count(), 0)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')

    def test_change_prod_qt_not_authenticated_user(self):
        session = self.client.session
        session['data'] = {'order': self.order_anonymous_user.id}
        session.save()
        pk = self.product2.id
        data = {'prod_num': 1}

        url = reverse('new', args=(pk, ))
        response = self.client.post(url, data=data)

        self.assertEqual(
            OrderedProduct.objects.filter(
                product=self.product2.id,
                order=self.order_anonymous_user.id).values('prod_num')[0]['prod_num'], 1)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')

    def test_change_prod_qt(self):
        self.client.force_login(self.test_user)
        pk = self.product1.id
        data = {'prod_num': 5}

        url = reverse('new', args=(pk, ))
        response = self.client.post(url, data=data)

        self.assertEqual(
            OrderedProduct.objects.filter(
                product=self.product1.id,
                order=self.order_user).values('prod_num')[0]['prod_num'], 5)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/cart/')
