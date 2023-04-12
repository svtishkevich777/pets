from django.urls import path
from shop.views import (
    product_list,
    product_detail,
    add_cart,
    cart_view,
    delete_cart_prod,
    change_prod_qt,
    order_product,
    send_order,
    user_login,
    register,
    logout_user,
    product_categories,
)

urlpatterns = [
    path('', product_list, name='product_list'),
    path('product_categories/<int:pk>', product_categories, name='product_list_by_category'),
    path('product_detail/<int:pk>', product_detail, name='product_detail'),
    path('add_cart/<int:product_id>', add_cart, name='add_cart'),
    path('cart/', cart_view, name='cart'),
    path('delete/', delete_cart_prod, name='delete_full_cart'),
    path('delete/<int:pk>', delete_cart_prod, name='delete'),
    path('change_qty/<int:pk>', change_prod_qt, name='new'),
    path('order/', order_product, name='order'),
    path('send/', send_order, name='send'),
    path('login/', user_login, name='login'),
    path('register/', register, name='register'),
    path('logout/', logout_user, name='logout'),


]
