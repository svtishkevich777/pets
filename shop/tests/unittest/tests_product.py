from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.shortcuts import HttpResponse

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

    @patch('shop.views.product.Category')
    @patch('shop.views.product.Product')
    @patch('shop.views.product.render')
    def test_product_list(self, mock_render,
                          mock_product,
                          mock_category):
        cart = {}
        url = reverse('product_list')
        mock_products = MagicMock()
        mock_ctegories = MagicMock()
        products_amount = 0
        mock_product.objects.all.return_value = mock_products
        mock_category.objects.all.return_value = mock_ctegories
        mock_render.return_value = HttpResponse()
        cart['products_amount'] = products_amount
        cart['categories'] = mock_ctegories
        cart['products'] = mock_products
        response = self.client.post(url, cart)
        mock_product.objects.all.assert_called_once_with()
        mock_category.objects.all.assert_called_once_with()
        mock_render.assert_called_once_with(response.wsgi_request,
                                            'base.html', cart)

    @patch('shop.views.product.Category')
    @patch('shop.views.product.Product')
    @patch('shop.views.product.Order')
    @patch('shop.views.product.render')
    def test_product_list_no_open_order_user(self,
                                             mock_render,
                                             mock_order,
                                             mock_product,
                                             mock_category):
        self.client.force_login(self.test_user)
        cart = {}
        mock_products = MagicMock()
        mock_categories = MagicMock()
        products_amount = 0
        url = reverse('product_list')
        mock_product.objects.all.return_value = mock_products
        mock_category.objects.all.return_value = mock_categories
        mock_order.objects.filter().last.return_value = None
        mock_render.return_value = HttpResponse()
        cart['products_amount'] = products_amount
        cart['categories'] = mock_categories
        cart['products'] = mock_products
        response = self.client.post(url, cart)
        mock_product.objects.all.assert_called_once_with()
        mock_category.objects.all.assert_called_once_with()
        mock_order.objects.filter().last.assert_called_once_with()
        mock_render.assert_called_with(response.wsgi_request,
                                       'base.html', cart)

    @patch('shop.views.product.Category')
    @patch('shop.views.product.Product')
    @patch('shop.views.product.Order')
    @patch('shop.views.product.render')
    def test_product_list_open_order_user(self,
                                          mock_render,
                                          mock_order,
                                          mock_product,
                                          mock_category):
        self.client.force_login(self.test_user)
        cart = {}
        mock_products = MagicMock()
        mock_categories = MagicMock()
        mock_order_id = MagicMock(id=1)
        count = 2
        url = reverse('product_list')
        mock_product.objects.all.return_value = mock_products
        mock_category.objects.all.return_value = mock_categories
        mock_order.objects.filter().last.return_value = mock_order_id
        mock_product.objects.filter().count.return_value = count
        mock_render.return_value = HttpResponse()
        cart['products_amount'] = count
        cart['categories'] = mock_categories
        cart['products'] = mock_products
        response = self.client.post(url, cart)
        mock_product.objects.all.assert_called_once_with()
        mock_category.objects.all.assert_called_once_with()
        mock_order.objects.filter().last.assert_called_once_with()
        mock_product.objects.filter().count.assert_called_once_with()
        mock_render.assert_called_with(response.wsgi_request,
                                       'base.html', cart)

    @patch('shop.views.product.Category')
    @patch('shop.views.product.Product')
    @patch('shop.views.product.render')
    def test_product_list_anonymous_order(self,
                                          mock_render,
                                          mock_product,
                                          mock_category):
        session = self.client.session
        session['data'] = {'order': 1}
        session.save()
        cart = {}
        mock_products = MagicMock()
        mock_categories = MagicMock()
        count = 2
        url = reverse('product_list')
        mock_product.objects.all.return_value = mock_products
        mock_category.objects.all.return_value = mock_categories
        mock_product.objects.filter().count.return_value = count
        mock_render.return_value = HttpResponse()
        cart['products_amount'] = count
        cart['categories'] = mock_categories
        cart['products'] = mock_products
        response = self.client.post(url, cart)
        mock_product.objects.all.assert_called_once_with()
        mock_category.objects.all.assert_called_once_with()
        mock_product.objects.filter().count.assert_called_once_with()
        mock_render.assert_called_with(response.wsgi_request,
                                       'base.html', cart)

    @patch('shop.views.product.get_object_or_404')
    @patch('shop.views.product.Category')
    @patch('shop.views.product.Product')
    @patch('shop.views.product.render')
    def test_product_categories(self,
                                mock_render,
                                mock_product,
                                mock_category,
                                mock_get_object_or_404):
        cart = {}
        mock_products = MagicMock()
        mock_get_object_or_404.return_value(mock_category, id=2)
        mock_product.objects.filter.return_value = mock_products
        mock_render.return_value = HttpResponse()
        url = reverse('product_list_by_category', args=(2,))
        cart['products'] = mock_products
        response = self.client.post(url, cart)
        mock_get_object_or_404.assert_called_once_with(mock_category, id=2)
        mock_product.objects.filter.assert_called_once_with(category=mock_get_object_or_404.return_value)
        mock_render.assert_called_with(response.wsgi_request,
                                       'base.html', cart)

    @patch('shop.views.product.get_object_or_404')
    @patch('shop.views.product.Product')
    @patch('shop.views.product.render')
    def test_product_detail(self,
                            mock_render,
                            mock_product,
                            mock_get_object_or_404):
        mock_get_object_or_404.return_value(mock_product, id=2, available=True)
        mock_render.return_value = HttpResponse()
        url = reverse('product_detail', args=(2,))
        response = self.client.post(url, {'product': mock_get_object_or_404})
        mock_get_object_or_404.assert_called_once_with(mock_product, id=2, available=True)
        mock_render.assert_called_with(response.wsgi_request,
                                       'shop/product/detail.html', {'product': mock_get_object_or_404.return_value})
