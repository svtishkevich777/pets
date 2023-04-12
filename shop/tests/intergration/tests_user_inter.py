from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from unittest.mock import patch

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

    def test_user_login(self):
        url = reverse('login')
        form = {
            'username': 'Pet',
            'password': 'petya12345'}
        response = self.client.post(url, form)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/')

    @patch('shop.views.user.messages')
    def test_user_login_2(self, mock_messages):
        form = {
            'username': 'Pet',
            'password': 'petya123'}

        url = reverse('login')
        response = self.client.post(url, form)

        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, 'Wrong login or password!')
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/login/')

    def test_user_login_form(self):
        url = reverse('login')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_register_user(self):
        form = {
            'username': 'Petya',
            'first_name': 'Pet',
            'last_name': 'Petr',
            'email': 'petya@gmail.com',
            'password': 'petya123',
            'password2': 'petya123'}

        url = reverse('register')
        response = self.client.post(url, form)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register_done.html')

    def test_register_user_incorrect_data(self):
        form = {
            'username': 'Petya',
            'first_name': 'Pet',
            'last_name': 'Petr',
            'email': 'petya@gmail.com',
            'password': 'petya123',
            'password2': 'petya1'}

        url = reverse('register')
        response = self.client.post(url, form)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')

    def test_register_user_form(self):
        url = reverse('register')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/register.html')
