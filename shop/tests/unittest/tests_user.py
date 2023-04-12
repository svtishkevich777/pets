from django.test import TestCase
from django.urls import reverse
from django.shortcuts import HttpResponse
from django.contrib.auth import get_user_model
from unittest.mock import patch, MagicMock

User = get_user_model()


class ModelTestCase(TestCase):
    def setUp(self):
        self.test_user = User.objects.create_user(username='Pet',
                                                  email='petya@gmail.com',
                                                  first_name='Petya',
                                                  last_name='Petro',
                                                  password='petya12345')

    @patch('shop.views.user.redirect')
    @patch('shop.views.user.login')
    @patch('shop.views.user.authenticate')
    @patch('shop.views.user.LoginForm')
    def test_user_login(self, mock_login_form,
                        mock_authenticate,
                        mock_login,
                        mock_redirect):
        mock_form = MagicMock()
        mock_login_form.return_value = mock_form
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'username': 'Pet',
            'password': 'petya12345'}
        user = MagicMock(is_active=True)
        mock_authenticate.return_value = user
        mock_form.is_active = True
        mock_login.return_value = True
        url = reverse('login')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url, mock_form.cleaned_data)
        mock_login.assert_called_once_with(response.wsgi_request, user)
        mock_authenticate.assert_called_once_with(
            username=mock_form.cleaned_data['username'],
            password=mock_form.cleaned_data['password'])
        mock_redirect.assert_called_with('/')

    @patch('shop.views.user.redirect')
    @patch('shop.views.user.authenticate')
    @patch('shop.views.user.LoginForm')
    @patch('shop.views.user.messages')
    def test_user_login_2(self, mock_messages,
                          mock_login_form,
                          mock_authenticate,
                          mock_redirect):
        mock_form = MagicMock()
        mock_login_form.return_value = mock_form
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'username': 'Pet',
            'password': 'petya123'}
        mock_authenticate.return_value = None
        url = reverse('login')
        mock_redirect.return_value = HttpResponse()
        response = self.client.post(url, mock_form.cleaned_data)
        mock_authenticate.assert_called_once_with(
            username=mock_form.cleaned_data['username'],
            password=mock_form.cleaned_data['password'])
        mock_messages.add_message.assert_called_with(
            response.wsgi_request, mock_messages.INFO, 'Wrong login or password!')
        mock_redirect.assert_called_with('login')

    @patch('shop.views.user.render')
    @patch('shop.views.user.LoginForm')
    def test_user_login_form(self, mock_login_form, mock_render):
        mock_login_form.is_valid.return_value = True
        url = reverse('login')
        mock_render.return_value = HttpResponse()
        mock_form = MagicMock()
        mock_login_form.return_value = mock_form
        response = self.client.get(url)
        mock_login_form.assert_called_once_with()
        mock_render.assert_called_with(response.wsgi_request, 'account/login.html', {'form': mock_form})

    @patch('shop.views.user.render')
    @patch('shop.views.user.User')
    @patch('shop.views.user.UserRegistrationForm')
    def test_register_user(self, mock_user_registration_form,
                           mock_user, mock_render):
        mock_form = MagicMock()
        mock_user_registration_form.return_value = mock_form
        mock_form.is_valid.return_value = True
        mock_form.cleaned_data = {
            'username': 'Petya',
            'first_name': 'Pet',
            'last_name': 'Petr',
            'email': 'petya@gmail.com',
            'password': 'petya123',
            'password2': 'petya123'}
        user = MagicMock(
            username='Petya',
            first_name='Pet',
            last_name='Petr',
            email='petya@gmail.com',
            password='petya123')
        mock_user.objects.create_user.return_value = user
        mock_render.return_value = HttpResponse()
        url = reverse('register')
        response = self.client.post(url, mock_form.cleaned_data)
        mock_user.objects.create_user.assert_called_once_with(username=user.username,
                                                              first_name=user.first_name,
                                                              last_name=user.last_name,
                                                              email=user.email,
                                                              password=user.password)
        mock_render.assert_called_once_with(response.wsgi_request,
                                            'account/register_done.html',
                                            {'new_user': user})

    @patch('shop.views.user.render')
    @patch('shop.views.user.UserRegistrationForm')
    def test_register_user_incorrect_data(self,
                                          mock_user_registration_form, mock_render):
        mock_form = MagicMock()
        mock_user_registration_form.return_value = mock_form
        mock_form.is_valid.return_value = False
        mock_render.return_value = HttpResponse()
        url = reverse('register')
        response = self.client.post(url)
        mock_render.assert_called_once_with(response.wsgi_request,
                                            'account/register.html',
                                            {'user_form': mock_form})

    @patch('shop.views.user.render')
    @patch('shop.views.user.UserRegistrationForm')
    def test_register_user_form(self, mock_user_registration_form, mock_render):
        mock_user_registration_form.is_valid.return_value = True
        url = reverse('register')
        mock_render.return_value = HttpResponse()
        mock_form = MagicMock()
        mock_user_registration_form.return_value = mock_form
        response = self.client.get(url)
        mock_user_registration_form.assert_called_once_with()
        mock_render.assert_called_once_with(response.wsgi_request,
                                            'account/register.html',
                                            {'user_form': mock_form})

    @patch('shop.views.user.redirect')
    @patch('shop.views.user.logout')
    def test_logout_user(self, mock_logout, mock_redirect):
        self.client.force_login(self.test_user)
        mock_logout.return_value = True
        url = reverse('logout')
        mock_redirect.return_value = HttpResponse()
        response = self.client.get(url)
        mock_logout.assert_called_with(response.wsgi_request)
        mock_redirect.assert_called_with('login')
