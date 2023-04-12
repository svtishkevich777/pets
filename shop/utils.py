from datetime import datetime
from typing import Optional

from django.conf import settings
from django.db.models import F, Sum
from django.core.mail import send_mail
from django.template.loader import render_to_string

from shop.models import Product, Order


def is_working_hours() -> bool:
    return settings.WORKING_END_HOURS > datetime.now().time().hour > settings.WORKING_START_HOURS


def product_selection_and_prices(order_id: int) -> dict:
    products = Product.objects.filter(orders=order_id, orders__status=settings.STATUS_IN_PROGRESS)
    products_qt = products.annotate(
        total_amount=F('order_products__prod_num'),
        total_price=F('order_products__prod_num') * F('price'),
    )
    all_data = products_qt.aggregate(all_price=Sum('total_price'), all_prod=Sum('total_amount'))
    data = {'products': products_qt, 'all_data': all_data}
    return data


def sending_a_letter_to_the_customer(data):
    html_message = render_to_string('shop/product/send_email.html', data)
    send_mail(
        subject='Ваш заказ',
        message='message for you',
        html_message=html_message,
        from_email=settings.EMAIL,
        recipient_list=[data['cd']['email'], 'sv@gmail.com'],  # admin email 'sv@gmail.com'
        fail_silently=False,
    )


def get_order_id_or_none(request) -> Optional[int]:
    if request.user.is_authenticated:
        order = Order.objects.filter(user=request.user, status=settings.STATUS_IN_PROGRESS).last()
        order_id = order and order.id
    else:
        order_id = None
        if 'data' in request.session.keys():
            data = request.session['data']
            order_id = data['order']
    return order_id
