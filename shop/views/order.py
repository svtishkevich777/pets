from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.conf import settings

from shop.models import Order
from shop.forms import UserFormOrder, AnonymousUserFormOrder
from shop.utils import (
    is_working_hours,
    product_selection_and_prices,
    sending_a_letter_to_the_customer,
    get_order_id_or_none,)


def order_product(request):
    if is_working_hours():
        add_product_order = get_order_id_or_none(request)
        if request.user.is_authenticated:
            form = UserFormOrder(request.POST)
        else:
            form = AnonymousUserFormOrder(request.POST)
        data = product_selection_and_prices(add_product_order)
        data['form'] = form
        return render(request, 'shop/product/order.html',  data)
    else:
        messages.add_message(request, messages.INFO, settings.SHOP_OPENING_HOURS)
        return redirect('cart')


@require_POST
def send_order(request):
    order = get_order_id_or_none(request)
    if request.user.is_authenticated:
        form = UserFormOrder(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            cd['first_name'] = request.user.first_name
            cd['last_name'] = request.user.last_name
            cd['email'] = request.user.email
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            return redirect('order')
    else:
        form = AnonymousUserFormOrder(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            return redirect('order')
    data = product_selection_and_prices(order)
    data.update(cd=cd)
    sending_a_letter_to_the_customer(data)
    Order.objects.filter(id=order).update(first_name=cd['first_name'],
                                          last_name=cd['last_name'],
                                          phone=cd['phone'],
                                          all_price=data['all_data']['all_price'],
                                          all_qtc=data['all_data']['all_prod'],
                                          city=cd['city'],
                                          address=cd['address'],
                                          comment=cd['comment'],
                                          created_at=cd['order_date'],
                                          status=settings.STATUS_COMPLETED)
    request.session.pop('data', None)
    return redirect('/')
