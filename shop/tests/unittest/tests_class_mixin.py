from django.test import TestCase
from django.core.exceptions import ValidationError

from shop.forms import LineInsertionCheckMixin


class MyCheckMixin(LineInsertionCheckMixin):
    def __init__(self, cleaned_data):
        self.cleaned_data = cleaned_data


class ModelTestCase(TestCase):
    def test_mixin_city(self):
        city = MyCheckMixin({'city': 'Minsk'})
        cd = city.clean_city()
        self.assertEqual(cd, 'Minsk')

    def test_mixin_not_city(self):
        city = MyCheckMixin({'city': '111'})
        with self.assertRaises(ValidationError) as cm:
            city.clean_city()
        the_exception = cm.exception
        self.assertEqual(the_exception.message,
                         'City name cannot be numeric!')

    def test_mixin_address(self):
        address = MyCheckMixin({'address': 'chapaeva, 5'})
        cd = address.clean_address()
        self.assertEqual(cd, 'chapaeva, 5')

    def test_mixin_not_address(self):
        address = MyCheckMixin({'address': '2222'})
        with self.assertRaises(ValidationError) as cm:
            address.clean_address()
        the_exception = cm.exception
        self.assertEqual(the_exception.message,
                         'The address must have a street name and house number!')
