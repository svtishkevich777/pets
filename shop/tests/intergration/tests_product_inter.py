from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.conf import settings

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
                                               status='in_progress')
        self.order_anonymous_user = Order.objects.create(user=None,
                                                         first_name='',
                                                         last_name='',
                                                         all_price=0,
                                                         all_qtc=0,
                                                         city='',
                                                         address='',
                                                         comment='',
                                                         status='in_progress')
        self.cart1 = OrderedProduct.objects.create(product=self.product1,
                                                   order=self.order_user,
                                                   prod_num=3)
        self.cart2 = OrderedProduct.objects.create(product=self.product2,
                                                   order=self.order_anonymous_user,
                                                   prod_num=5)

    def test_product_list(self):
        categories = Category.objects.all()
        products = Product.objects.all()

        url = reverse('product_list')
        response = self.client.get(url)

        self.assertEqual(len(categories), 2)
        self.assertEqual(len(products), 2)
        self.assertEqual(categories[0].name, 'biscuit')
        self.assertEqual(products[0].name, 'Nestle')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    def test_product_list_check_order_user(self):
        self.client.force_login(self.test_user)
        check_order = Order.objects.filter(user=self.test_user, status=settings.STATUS_IN_PROGRESS).last()
        products_amount = Product.objects.filter(orders=check_order).count()

        url = reverse('product_list')
        response = self.client.get(url)

        self.assertEqual(products_amount, 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    def test_product_list_check_order_anonymous_user(self):
        session = self.client.session
        session['data'] = {'order': self.order_anonymous_user.id}
        session.save()

        url = reverse('product_list')
        response = self.client.get(url, session)

        products_amount = Product.objects.filter(orders=session['data']['order']).count()
        self.assertEqual(products_amount, 1)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')

    def test_product_categories(self):
        pk = self.category1.id
        url = reverse('product_list_by_category', args=(pk, ))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'base.html')
        self.assertEqual(self.category1.name, 'chocolate')
        self.assertEqual(self.category1.products.count(), 1)
        Product.objects.create(name='Nats', price=2,
                               stock=3, category=self.category1,
                               image='media/01168209.n_1_190x190.png.jpg')
        self.assertEqual(self.category1.products.count(), 2)

    def test_product_detail(self):
        pk = self.product1.id

        url = reverse('product_detail', args=(pk, ))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'shop/product/detail.html')
        self.assertEqual(self.product1.id, 1)
        self.assertEqual(self.product1.price, 3)
        self.assertEqual(self.product1.stock, 5)
        self.assertEqual(self.product1.image, 'media/00015718.n_1_190x190.png.jpg')
