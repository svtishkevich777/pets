from rest_framework.viewsets import ModelViewSet
from shop.models import Category, Product, Order, OrderedProduct
from api.serializers import CategorySerializer, ProductSerializer, OrderSerializer, OrderedProductSerializer
from rest_framework import permissions


def get_user_permissions(self):
    if self.request.method in ['POST', 'PATCH', 'PUT', 'DELETE']:
        return [permissions.IsAdminUser()]
    return [permissions.IsAuthenticatedOrReadOnly()]


class APICategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
        return get_user_permissions(self)


class APIProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        return get_user_permissions(self)


class APIOrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def get_queryset(self):
        queryset = Order.objects.filter(user=self.request.user)
        return queryset

    def get_permissions(self):
        return get_user_permissions(self)


class APIOrderedProductViewSet(ModelViewSet):
    queryset = OrderedProduct.objects.all()
    serializer_class = OrderedProductSerializer

    def get_queryset(self):
        queryset = OrderedProduct.objects.filter(order__user=self.request.user)
        return queryset

    def get_permissions(self):
        return get_user_permissions(self)
