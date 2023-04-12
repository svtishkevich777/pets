from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import (
    APIProductViewSet,
    APIOrderViewSet,
    APIOrderedProductViewSet,
    APICategoryViewSet,
    )


router = DefaultRouter()
router.register('category', APICategoryViewSet, basename='category')
router.register('product', APIProductViewSet)
router.register('order', APIOrderViewSet)
router.register('order_product', APIOrderedProductViewSet)


urlpatterns = [
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('', include(router.urls)),
]
