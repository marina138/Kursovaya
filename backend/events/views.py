from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend

from .models import Product, Category
from .filters import ProductFilter
from .forms import AddToCartForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from rest_framework.generics import ListAPIView
from .models import Product
from rest_framework import generics
from .serializers import ProductSerializer
from .filters import ProductFilter
from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter


def index(request):
    return render(request, 'index.html')


def catalog_view(request):
    product_filter = ProductFilter(request.GET, queryset=Product.objects.all())
    products = product_filter.qs  # отфильтрованные товары
    return render(request, 'catalog.html', {
        'filter': product_filter,
        'products': products
    })


@login_required
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': str(product.price),
            'image': product.image.url if product.image else '',
            'quantity': 1,
        }

    request.session['cart'] = cart
    request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER', 'catalog'))  # возвращает на предыдущую страницу


def view_cart(request):
    cart = request.session.get('cart', {})

    total = Decimal('0')
    for item in cart.values():
        total += Decimal(item['price']) * item['quantity']

    return render(request, 'cart.html', {
        'cart': cart,
        'total': total,
    })


def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = cart.items.all()
    else:
        cart_items = []
    return render(request, 'cart_detail.html', {'cart_items': cart_items})


@require_POST
def increase_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
        request.session['cart'] = cart
    return redirect('cart')


@require_POST
def decrease_quantity(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if cart[str(product_id)]['quantity'] > 1:
            cart[str(product_id)]['quantity'] -= 1
        else:
            del cart[str(product_id)]
        request.session['cart'] = cart
    return redirect('cart')


def checkout(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')

        # Можно сохранить заказ в БД

        request.session['cart'] = {}
        request.session.modified = True

        return render(request, 'checkout.html', {'message': 'Заказ оформлен'})

    return render(request, 'checkout.html')

