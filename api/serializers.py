from rest_framework import serializers
from shop.models import Category, Product, Order, OrderedProduct


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderedProduct
        fields = '__all__'
