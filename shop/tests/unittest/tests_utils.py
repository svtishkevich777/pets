from django.test import TestCase

from unittest.mock import patch, MagicMock

from shop.utils import \
    (is_working_hours,
     product_selection_and_prices,
     sending_a_letter_to_the_customer,
     get_order_id_or_none)

import os

from django.conf import settings

os.environ['DJANGO_SETTINGS_MODULE'] = 'src.settings'


class ModelTestCase(TestCase):
    @patch('shop.utils.datetime')
    def test_is_working_hours_true(self, mock_datetime):
        mock_datetime.now().time().hour = 9
        data = is_working_hours()
        self.assertTrue(data)

    @patch('shop.utils.datetime')
    def test_is_working_hours_false(self, mock_datetime):
        mock_datetime.now().time().hour = 4
        data = is_working_hours()
        self.assertFalse(data)

    @patch('shop.utils.Product')
    @patch('shop.utils.F')
    @patch('shop.utils.Sum')
    def test_product_selection_and_prices(self, mock_sum, mock_f, mock_products):
        order_id = 2
        products = MagicMock()
        products_qt = MagicMock()
        mock_products.objects.filter.return_value = products
        products.annotate.return_value = products_qt
        products_qt.aggregate.return_value = {'asdf': 'asdf'}
        mock_f.side_effect = (3, 2, 5)
        mock_sum.side_effect = (10, 20)
        data = {'products': products.annotate.return_value, 'all_data': products_qt.aggregate.return_value}
        result_data = product_selection_and_prices(order_id)
        mock_products.objects.filter.assert_called_once_with(
            orders=order_id, orders__status=settings.STATUS_IN_PROGRESS)
        products.annotate.assert_called_once_with(total_amount=3, total_price=10)
        products_qt.aggregate.assert_called_once_with(all_price=10, all_prod=20)
        self.assertEqual(result_data, data)

    @patch('shop.utils.send_mail')
    @patch('shop.utils.render_to_string')
    def test_sending_a_letter_to_the_customer(self,
                                              mock_render_to_string,
                                              mock_send_mail):
        mock_render_to_string.return_value = '<html><body>Hell world</body></html>'
        data = {'cd': {'email': 'aaa@gmail.com'}}
        sending_a_letter_to_the_customer(data)
        mock_render_to_string.assert_called_once_with('shop/product/send_email.html', data)
        mock_send_mail.assert_called_once_with(
            subject='Ваш заказ',
            message='message for you',
            html_message=mock_render_to_string.return_value,
            from_email=settings.EMAIL,
            recipient_list=[data['cd']['email'], 'sv@gmail.com'],
            fail_silently=False,
        )

    @patch('shop.utils.Order')
    def test_get_order_id_or_none_user_true(self, mock_order):
        mock_order_id = MagicMock(id=1)
        mock_order.objects.filter().last.return_value = mock_order_id
        request = MagicMock()
        request.user.is_authenticated = True
        result = get_order_id_or_none(request)
        mock_order.objects.filter().last.assert_called_once_with()
        self.assertEqual(result, 1)

    @patch('shop.utils.Order')
    def test_get_order_id_or_none_user_None(self, mock_order):
        mock_order_id = MagicMock(id=None)
        mock_order.objects.filter().last.return_value = mock_order_id
        request = MagicMock()
        request.user.is_authenticated = True
        result = get_order_id_or_none(request)
        mock_order.objects.filter().last.assert_called_once_with()
        self.assertEqual(result, None)

    def test_get_order_id_or_none_user_anonymous_true(self):
        session = self.client.session
        session['data'] = {'order': 2}
        session.save()
        user_anonymous = MagicMock()
        user_anonymous.user.is_authenticated = False
        user_anonymous.session.keys.return_value = 'data'
        user_anonymous.session = session
        result = get_order_id_or_none(user_anonymous)
        self.assertEqual(result, 2)

    def test_get_order_id_or_none_user_anonymous_none(self):
        user_anonymous = MagicMock()
        user_anonymous.user.is_authenticated = False
        user_anonymous.session.keys.return_value = []
        result = get_order_id_or_none(user_anonymous)
        self.assertEqual(result, None)
