from django.shortcuts import render, get_object_or_404

from shop.models import Category, Product, Order
from src.settings import STATUS_IN_PROGRESS


def product_list(request):
    cart = {}
    categories = Category.objects.all()
    products = Product.objects.all()
    products_amount = 0
    if request.user.is_authenticated:
        check_order = Order.objects.filter(user=request.user, status=STATUS_IN_PROGRESS).last()
        if check_order:
            products_amount = Product.objects.filter(orders=check_order.id).count()
    else:
        if 'data' in request.session.keys():
            data = request.session['data']
            products_amount = Product.objects.filter(orders=data['order']).count()
    cart['products_amount'] = products_amount
    cart['categories'] = categories
    cart['products'] = products
    return render(request, 'base.html',  cart)


def product_categories(request, pk):
    cart = {}
    category = get_object_or_404(Category, id=pk)
    products = Product.objects.filter(category=category)
    cart['products'] = products
    return render(request, 'base.html', cart)


def product_detail(request, pk):
    product = get_object_or_404(Product, id=pk, available=True)
    return render(request, 'shop/product/detail.html', {'product': product})
