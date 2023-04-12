from django.contrib.auth import get_user_model
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True, unique=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=200, db_index=True)
    slug = models.SlugField(max_length=200, db_index=True)
    image = models.ImageField(upload_to='products/%Y/%m/%d', blank=True)
    description = models.TextField(blank=True)
    price = models.FloatField()
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    STATUS_NEW = 'new'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETED = 'delivered'
    STATUS_CHOICES = (
        (STATUS_NEW, 'new'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_COMPLETED, 'delivered'))

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)
    phone = PhoneNumberField(blank=True)
    all_price = models.FloatField(blank=True, null=True)
    all_qtc = models.PositiveIntegerField(blank=True, null=True)
    city = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=1024, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=100, verbose_name='status_order', choices=STATUS_CHOICES, default=STATUS_NEW)
    products = models.ManyToManyField('Product', through='OrderedProduct', related_name='orders')


class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_products')
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_products', null=True, blank=True)
    prod_num = models.PositiveIntegerField(default=0)
    in_cart = models.BooleanField(default=False)
