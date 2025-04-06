from django.shortcuts import render
from .models import Product, Category
from .filters import ProductFilter
from .forms import AddToCartForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Cart, CartItem
from django.contrib.auth.decorators import login_required


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
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)

    # Получаем или создаем корзину пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Проверяем, есть ли уже этот товар в корзине
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    # Если товар есть в корзине, увеличиваем его количество
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart:cart_detail')  # Перенаправление на страницу корзины


@login_required
def cart_detail(request):
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_items = cart.items.all()
    else:
        cart_items = []
    return render(request, 'events/cart_detail.html', {'cart_items': cart_items})
