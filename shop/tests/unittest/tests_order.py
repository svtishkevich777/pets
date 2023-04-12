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

    @patch('shop.views.order.redirect')
    @patch('shop.views.order.messages')
    @patch('shop.views.order.is_working_hours')
    def test_shop_opening_hours(self,
                                mock_is_working_hours,
                                mock_messages,
                                mock_redirect):
        mock_is_working_hours.return_value = False

        url = reverse('order')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)

        mock_messages.add_message.assert_called_once_with(
            response.wsgi_request, mock_messages.INFO, settings.SHOP_OPENING_HOURS)
        mock_redirect.assert_called_with('cart')

    @patch('shop.views.order.render')
    @patch('shop.views.order.product_selection_and_prices')
    @patch('shop.views.order.UserFormOrder')
    @patch('shop.views.order.get_order_id_or_none')
    @patch('shop.views.order.is_working_hours')
    def test_order_product_user(self,
                                mock_is_working_hours,
                                mock_get_order_id_or_none,
                                mock_user_form_order,
                                mock_product_and_prices,
                                mock_render):
        self.client.force_login(self.test_user)
        mock_is_working_hours.return_value = True
        mock_get_order_id_or_none.return_value = 2
        mock_form = MagicMock()
        mock_user_form_order.return_value = mock_form
        mock_product_and_prices.return_value = {'data': 1}
        data = mock_product_and_prices.return_value
        data['form'] = mock_form

        url = reverse('order')
        mock_render.return_value = HttpResponse()
        response = self.client.post(url)

        mock_is_working_hours.assert_called_once_with()
        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_product_and_prices.assert_called_once_with(mock_get_order_id_or_none.return_value)
        mock_render.assert_called_with(response.wsgi_request,
                                       'shop/product/order.html', data)

    @patch('shop.views.order.render')
    @patch('shop.views.order.product_selection_and_prices')
    @patch('shop.views.order.AnonymousUserFormOrder')
    @patch('shop.views.order.get_order_id_or_none')
    @patch('shop.views.order.is_working_hours')
    def test_order_product_anonymous_user(self,
                                          mock_is_working_hours,
                                          mock_get_order_id_or_none,
                                          mock_anonymous_user_form_order,
                                          mock_product_and_prices,
                                          mock_render):
        mock_is_working_hours.return_value = True
        mock_get_order_id_or_none.return_value = 2
        mock_form = MagicMock()
        mock_anonymous_user_form_order.return_value = mock_form
        mock_product_and_prices.return_value = {'data': 1}
        data = mock_product_and_prices.return_value
        data['form'] = mock_form

        url = reverse('order')
        mock_render.return_value = HttpResponse()
        response = self.client.post(url)

        mock_is_working_hours.assert_called_once_with()
        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_product_and_prices.assert_called_once_with(mock_get_order_id_or_none.return_value)
        mock_render.assert_called_with(response.wsgi_request,
                                       'shop/product/order.html', data)

    @patch('shop.views.order.redirect')
    @patch('shop.views.order.Order')
    @patch('shop.views.order.sending_a_letter_to_the_customer')
    @patch('shop.views.order.product_selection_and_prices')
    @patch('shop.views.order.UserFormOrder')
    @patch('shop.views.order.get_order_id_or_none')
    def test_send_order_user(self,
                             mock_get_order_id_or_none,
                             mock_user_form_order,
                             mock_product_and_prices,
                             mock_sending_letter,
                             mock_order,
                             mock_redirect):
        self.client.force_login(self.test_user)
        mock_get_order_id_or_none.return_value = 2
        mock_form = MagicMock()
        mock_user_form_order.return_value = mock_form
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'city': 'Minsk',
            'address': 'chapaeva, 5',
            'phone': '+375291000000',
            'all_price': 5,
            'all_qtc': 10,
            'status': 'delivered',
            'order_date': '20.10.21',
            'comment': 'OK'
        }
        order = MagicMock(
            city='Minsk',
            address='chapaeva, 5',
            phone='+375291000000',
            order_date='20.10.21',
            comment='OK')
        data = {'products': 2, 'all_data': {'all_price': 9, 'all_prod': 4}}
        mock_product_and_prices.return_value = data
        mock_sending_letter.return_value = data
        mock_one_order = MagicMock(id=1)
        mock_order.objects.filter.return_value = mock_one_order
        mock_order.objects.filter().update.return_value = order

        url = reverse('send')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url, mock_form.cleaned_data)

        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_user_form_order.assert_called_once()
        mock_product_and_prices.assert_called_once_with(mock_get_order_id_or_none.return_value)
        mock_sending_letter.assert_called_once_with(data)
        mock_order.objects.filter().update.assert_called_once_with(
            first_name='Petya',
            last_name='Petro',
            phone='+375291000000',
            all_price=9,
            all_qtc=4,
            city='Minsk',
            address='chapaeva, 5',
            comment='OK',
            created_at='20.10.21',
            status=settings.STATUS_COMPLETED)
        mock_redirect.assert_called_with('/')

    @patch('shop.views.order.redirect')
    @patch('shop.views.order.Order')
    @patch('shop.views.order.sending_a_letter_to_the_customer')
    @patch('shop.views.order.product_selection_and_prices')
    @patch('shop.views.order.AnonymousUserFormOrder')
    @patch('shop.views.order.get_order_id_or_none')
    def test_send_order_anonymous_user(self,
                                       mock_get_order_id_or_none,
                                       mock_anonymous_user_form_order,
                                       mock_product_and_prices,
                                       mock_sending_letter,
                                       mock_order,
                                       mock_redirect):
        mock_get_order_id_or_none.return_value = 2
        mock_form = MagicMock()
        mock_anonymous_user_form_order.return_value = mock_form
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'first_name': 'Pet',
            'last_name': 'Petr',
            'email': 'petya@gmail.com',
            'city': 'Minsk',
            'address': 'chapaeva, 5',
            'phone': '+375291000000',
            'all_price': 5,
            'all_qtc': 10,
            'status': 'delivered',
            'order_date': '20.10.21',
            'comment': 'OK'
        }
        order = MagicMock(
            first_name='Pet',
            last_name='Petr',
            email='petya@gmail.com',
            city='Minsk',
            address='chapaeva, 5',
            phone='+375291000000',
            order_date='20.10.21',
            comment='OK')
        mock_product_and_prices.return_value = {'products': 2, 'all_data': {'all_price': 5, 'all_prod': 10}}
        data = mock_product_and_prices.return_value
        data.update(order)
        mock_sending_letter.return_value = data
        mock_one_order = MagicMock(id=1)
        mock_order.objects.filter.return_value = mock_one_order
        mock_order.objects.filter().update.return_value = order

        url = reverse('send')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url, mock_form.cleaned_data)

        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_anonymous_user_form_order.assert_called_once()
        mock_product_and_prices.assert_called_once_with(mock_get_order_id_or_none.return_value)
        mock_sending_letter.assert_called_once_with(data)
        mock_order.objects.filter().update.assert_called_once_with(
            first_name='Pet',
            last_name='Petr',
            phone='+375291000000',
            all_price=5,
            all_qtc=10,
            city='Minsk',
            address='chapaeva, 5',
            comment='OK',
            created_at='20.10.21',
            status=settings.STATUS_COMPLETED)
        mock_redirect.assert_called_with('/')

    @patch('shop.views.order.redirect')
    @patch('shop.views.order.messages')
    @patch('shop.views.order.UserFormOrder')
    @patch('shop.views.order.get_order_id_or_none')
    def test_send_order_user_not_valid_form(self,
                                            mock_get_order_id_or_none,
                                            mock_user_form_order,
                                            mock_messages,
                                            mock_redirect):
        self.client.force_login(self.test_user)
        mock_get_order_id_or_none.return_value = 2
        mock_form = MagicMock()
        mock_user_form_order.return_value = mock_form
        mock_form.is_valid.return_value = False

        url = reverse('send')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)

        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_messages.add_message.assert_called_once_with(
            response.wsgi_request, mock_messages.ERROR, mock_form.errors)
        mock_redirect.assert_called_with('order')

    @patch('shop.views.order.redirect')
    @patch('shop.views.order.messages')
    @patch('shop.views.order.AnonymousUserFormOrder')
    @patch('shop.views.order.get_order_id_or_none')
    def test_send_order_anonymous_user_not_valid_form(self,
                                                      mock_get_order_id_or_none,
                                                      mock_anonymous_user_form_order,
                                                      mock_messages,
                                                      mock_redirect):
        mock_get_order_id_or_none.return_value = 2
        mock_form = MagicMock()
        mock_anonymous_user_form_order.return_value = mock_form
        mock_form.is_valid.return_value = False

        url = reverse('send')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url)

        mock_get_order_id_or_none.assert_called_once_with(response.wsgi_request)
        mock_messages.add_message.assert_called_once_with(
            response.wsgi_request, mock_messages.ERROR, mock_form.errors)
        mock_redirect.assert_called_with('order')
