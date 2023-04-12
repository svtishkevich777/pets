from django.forms import Form, CharField, EmailField, DateTimeField, PasswordInput, DateInput, IntegerField
from phonenumber_field.formfields import PhoneNumberField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from shop.models import Product


class QuantityProductForm(Form):
    prod_num = IntegerField(min_value=1)
    prod_id = IntegerField(min_value=1)

    def clean_prod_num(self):
        qtc = self.cleaned_data['prod_num']
        prod_id = self.data['prod_id']
        product_stock = Product.objects.get(id=prod_id).stock
        if product_stock < qtc:
            raise ValidationError('This number of products is not in stock!')
        return qtc


class LineInsertionCheckMixin:
    def clean_city(self):
        cd = self.cleaned_data['city']
        if cd.isdigit():
            raise ValidationError('City name cannot be numeric!')
        return cd

    def clean_address(self):
        cd = self.cleaned_data['address']
        if cd.isdigit():
            raise ValidationError('The address must have a street name and house number!')
        return cd


class UserFormOrder(LineInsertionCheckMixin, Form):
    city = CharField(min_length=2, max_length=20)
    address = CharField(min_length=5, max_length=50)
    phone = PhoneNumberField()
    order_date = DateTimeField(widget=DateInput(attrs={'type': 'datetime-local'}))
    comment = CharField(required=False)


class AnonymousUserFormOrder(LineInsertionCheckMixin, Form):
    first_name = CharField(min_length=2, max_length=20)
    last_name = CharField(min_length=2, max_length=20)
    email = EmailField()
    city = CharField(min_length=2, max_length=20)
    address = CharField(min_length=5, max_length=50)
    phone = PhoneNumberField()
    order_date = DateTimeField(widget=DateInput(attrs={'type': 'datetime-local'}))
    comment = CharField(required=False)


class LoginForm(Form):
    username = CharField()
    password = CharField(widget=PasswordInput)


class UserRegistrationForm(Form):
    username = CharField(max_length=25)
    first_name = CharField(min_length=2, max_length=15)
    last_name = CharField()
    email = EmailField()
    password = CharField(label='Password', widget=PasswordInput)
    password2 = CharField(label='Repeat password', widget=PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 'password2')

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise ValidationError('Passwords don\'t match!')
        return cd['password2']

    def clean_username(self):
        cd = self.cleaned_data['username']
        if User.objects.filter(username=cd).exists():
            raise ValidationError('Such user already exists!')
        return cd


