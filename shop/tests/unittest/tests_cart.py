from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import HttpResponse
from django.conf import settings

from unittest.mock import patch, MagicMock

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

    @patch('shop.views.cart.messages')
    @patch('shop.views.cart.redirect')
    @patch('shop.views.cart.OrderedProduct')
    @patch('shop.views.cart.Order')
    @patch('shop.views.cart.Product')
    def test_add_product_to_cart_user(self, mock_product,
                                      mock_order,
                                      mock_order_product,
                                      mock_redirect,
                                      mock_messages):
        self.client.force_login(self.test_user)
        mock_products = MagicMock()
        mock_one_order = MagicMock()
        mock_one_order_products = MagicMock(prod_num=0)
        mock_product.objects.get.return_value = mock_products
        mock_order.objects.get_or_create.return_value = mock_one_order, True
        mock_order_product.objects.get_or_create.return_value = mock_one_order_products, True
        url = reverse('add_cart', args=(2,))
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)
        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, settings.PRODUCT_ADDED)
        mock_product.objects.get.assert_called_once_with(id=2)
        mock_order.objects.get_or_create.assert_called_once_with(user=self.test_user,
                                                                 status=settings.STATUS_IN_PROGRESS)
        mock_order_product.objects.get_or_create.assert_called_once_with(in_cart=True,
                                                                         product=mock_products,
                                                                         order=mock_one_order)
        self.assertEqual(mock_one_order_products.prod_num, 1)
        mock_redirect.assert_called_once_with('product_list')

    @patch('shop.views.cart.messages')
    @patch('shop.views.cart.redirect')
    @patch('shop.views.cart.OrderedProduct')
    @patch('shop.views.cart.Order')
    @patch('shop.views.cart.Product')
    def test_add_product_to_cart_anonymous_user(self, mock_product,
                                                mock_order,
                                                mock_order_product,
                                                mock_redirect,
                                                mock_messages):
        mock_products = MagicMock()
        mock_one_order = MagicMock(id=1)
        mock_one_order_products = MagicMock(prod_num=0)
        mock_product.objects.get.return_value = mock_products
        mock_order.objects.get_or_create.return_value = mock_one_order, True
        mock_order_product.objects.get_or_create.return_value = mock_one_order_products, True
        url = reverse('add_cart', args=(1, ))
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)
        mock_product.objects.get.assert_called_once_with(id=1)
        mock_order.objects.get_or_create.assert_called_once_with(user=None,
                                                                 status=settings.STATUS_IN_PROGRESS)
        mock_order_product.objects.get_or_create.assert_called_once_with(in_cart=True,
                                                                         product=mock_products,
                                                                         order=mock_one_order)
        mock_messages.add_message.assert_called_once_with(
            response.wsgi_request, mock_messages.INFO, settings.PRODUCT_ADDED)
        self.assertEqual(mock_one_order_products.prod_num, 1)
        mock_redirect.assert_called_once_with('product_list')

    @patch('shop.views.cart.render')
    @patch('shop.views.cart.get_order_id_or_none')
    def test_cart_view(self, mock_get_order_or_none, mock_render):
        url = reverse('cart')
        data = None
        mock_get_order_or_none.return_value = None
        mock_render.return_value = HttpResponse()
        response = self.client.post(url)
        mock_get_order_or_none.assert_called_once_with(response.wsgi_request)
        mock_render.assert_called_once_with(response.wsgi_request,
                                            'shop/product/cart.html', data)

    @patch('shop.views.cart.render')
    @patch('shop.views.cart.product_selection_and_prices')
    @patch('shop.views.cart.get_order_id_or_none')
    def test_cart_view_products(self, mock_get_order_or_none,
                                mock_product_and_prices,
                                mock_render):
        url = reverse('cart')
        mock_get_order_or_none.return_value = 2
        mock_product_and_prices.return_value = {'data': 1}
        data = mock_product_and_prices.return_value
        mock_render.return_value = HttpResponse()
        response = self.client.post(url)
        mock_get_order_or_none.assert_called_once_with(response.wsgi_request)
        mock_product_and_prices.assert_called_once_with(2)
        mock_render.assert_called_once_with(response.wsgi_request,
                                            'shop/product/cart.html', data)

    @patch('shop.views.cart.redirect')
    @patch('shop.views.cart.OrderedProduct')
    @patch('shop.views.cart.get_order_id_or_none')
    @patch('shop.views.cart.QuantityProductForm')
    def test_change_prod_qt(self, mock_product_form,
                            mock_get_order_id_or_none,
                            mock_order_product,
                            mock_redirect):
        mock_form = MagicMock()
        mock_order_product_qt = MagicMock(prod_num=5)
        mock_product_form.return_value = mock_form
        mock_form.is_valid.return_value = True
        mock_get_order_id_or_none.return_value = 2
        mock_order_product.objects.get.return_value = mock_order_product_qt
        mock_form.cleaned_data = {
            'prod_num': 1,
            'prod_id': 2}
        url = reverse('new', args=(1, ))
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url, mock_form.cleaned_data)
        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_order_product.objects.get.assert_called_once_with(
            product=1, order=mock_get_order_id_or_none.return_value)
        mock_redirect.assert_called_once_with('cart')

    @patch('shop.views.cart.redirect')
    @patch('shop.views.cart.messages')
    @patch('shop.views.cart.QuantityProductForm')
    def test_change_prod_qt_errors(self, mock_product_form,
                                   mock_messages,
                                   mock_redirect):
        mock_form = MagicMock()
        mock_product_form.return_value = mock_form
        mock_form.is_valid.return_value = False
        mock_form.cleaned_data = {
            'prod_num': 1,
            'prod_id': 2}
        url = reverse('new', args=(1,))
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url, mock_form.cleaned_data)
        mock_messages.add_message.assert_called_once_with(
            response.wsgi_request, mock_messages.ERROR, mock_form.errors)
        mock_redirect.assert_called_with('cart')

    @patch('shop.views.cart.redirect')
    @patch('shop.views.cart.OrderedProduct')
    @patch('shop.views.cart.get_order_id_or_none')
    def test_delete_cart_prod(self, mock_get_order_id_or_none,
                              mock_order_product,
                              mock_redirect):
        mock_get_order_id_or_none.return_value = 2
        url = reverse('delete', args=(1, ))
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)
        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_order_product.objects.filter.assert_called_once_with(
            product=1, order=mock_get_order_id_or_none.return_value)
        mock_order_product.objects.filter().delete.assert_called_once()
        mock_redirect.assert_called_with('cart')

    @patch('shop.views.cart.redirect')
    @patch('shop.views.cart.OrderedProduct')
    @patch('shop.views.cart.get_order_id_or_none')
    def test_delete_cart_prod_all(self, mock_get_order_id_or_none,
                                  mock_order_product,
                                  mock_redirect):
        mock_get_order_id_or_none.return_value = 2
        url = reverse('delete_full_cart')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)
        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_order_product.objects.filter.assert_called_once_with(
            order=mock_get_order_id_or_none.return_value)
        mock_order_product.objects.filter().delete.assert_called_once()
        mock_redirect.assert_called_with('cart')
