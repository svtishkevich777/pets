from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings

from shop.models import Product, Order, OrderedProduct
from shop.utils import product_selection_and_prices, get_order_id_or_none
from shop.forms import QuantityProductForm


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    if request.user.is_authenticated:
        check_order, _ = Order.objects.get_or_create(user=request.user, status=settings.STATUS_IN_PROGRESS)
    else:
        check_order, _ = Order.objects.get_or_create(user=None, status=settings.STATUS_IN_PROGRESS)
        data = {'order': check_order.id}
        request.session['data'] = data
    cart_prod, _ = OrderedProduct.objects.get_or_create(in_cart=True, product=product, order=check_order)
    cart_prod.prod_num += 1
    cart_prod.save()
    messages.add_message(request, messages.INFO, settings.PRODUCT_ADDED)
    return redirect('product_list')


def cart_view(request):
    order_id = get_order_id_or_none(request)
    data = None
    if order_id is not None:
        data = product_selection_and_prices(order_id)
    return render(request, 'shop/product/cart.html', data)


@require_POST
def change_prod_qt(request, pk):
    data = request.POST.copy()
    data['prod_id'] = pk
    form = QuantityProductForm(data)
    if form.is_valid():
        order_id = get_order_id_or_none(request)
        cart_prod = OrderedProduct.objects.get(product=pk, order=order_id)
        cd = form.cleaned_data
        cart_prod.prod_num = cd['prod_num']
        cart_prod.save()
    else:
        messages.add_message(request, messages.ERROR, form.errors)
    return redirect('cart')


@require_POST
def delete_cart_prod(request, pk=None):
    order_id = get_order_id_or_none(request)
    if pk:
        OrderedProduct.objects.filter(product=pk, order=order_id).delete()
    else:
        OrderedProduct.objects.filter(order=order_id).delete()
    return redirect('cart')
