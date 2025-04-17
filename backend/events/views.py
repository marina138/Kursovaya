from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
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
from .serializers import ProductSerializer, OrderSerializer
from .filters import ProductFilter
from rest_framework import viewsets
from .models import Category
from .serializers import CategorySerializer
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order, OrderItem, Product, Customer
from django.core.exceptions import ValidationError
import logging
logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def place_order(request):
    try:
        if not request.body:
            return JsonResponse({'error': 'Тело запроса пустое'}, status=400)

        data = json.loads(request.body)
        name = data.get('name')
        phone = data.get('phone')
        email = data.get('email')
        items = data.get('items', [])

        # Валидация
        if not all([name, phone, email]):
            return JsonResponse({'error': 'Все поля обязательны'}, status=400)
        if len(name) < 3:
            return JsonResponse({'error': 'ФИО должно быть не короче 3 символов'}, status=400)
        if not phone.startswith('+7') or len(phone) != 12:
            return JsonResponse({'error': 'Введите номер в формате +7XXXXXXXXXX'}, status=400)
        if not email or '@' not in email or '.' not in email:
            return JsonResponse({'error': 'Введите корректный адрес электронной почты'}, status=400)
        if not items:
            return JsonResponse({'error': 'Корзина пуста'}, status=400)

        # Логи для отладки
        print("Полученные данные:", data)

        # Создание клиента
        customer, created = Customer.objects.get_or_create(
            phone=phone,
            defaults={'phone': phone, 'email': email}
        )
        if not created and email and customer.email != email:
            customer.email = email
            customer.save()

        # Создание заказа
        order = Order(address="Адрес по умолчанию")  # Временный адрес, так как поле удалено из формы
        try:
            order.full_clean()
            order.save()
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

        # Сохранение товаров заказа
        for item in items:
            try:
                product = Product.objects.get(id=item['product_id'])
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    quantity=item['quantity'],
                    price=item['price']
                )
            except Product.DoesNotExist:
                return JsonResponse({'error': f'Товар с ID {item["product_id"]} не найден'}, status=400)

        # Очистка корзины
        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True

        return JsonResponse({'message': 'Заказ успешно оформлен!'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный формат JSON'}, status=400)
    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)

# Остальные функции views.py без изменений
def get_cart(request):
    cart = request.session.get('cart', {})
    total = sum(float(item['price']) * item['quantity'] for item in cart.values())
    return JsonResponse({
        'cart': cart,
        'total': total,
    })

@csrf_exempt
@require_POST
def update_cart(request, product_id):
    data = json.loads(request.body)
    action = data.get('action')
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        if action == 'increment':
            cart[str(product_id)]['quantity'] += 1
        elif action == 'decrement':
            cart[str(product_id)]['quantity'] -= 1
            if cart[str(product_id)]['quantity'] <= 0:
                del cart[str(product_id)]
    request.session['cart'] = cart
    request.session.modified = True
    return JsonResponse({'message': 'Корзина обновлена'})

@api_view(['POST'])
def create_order(request):
    data = request.data
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    address = data.get('address')
    items = data.get('items', [])

    if not all([name, phone, email, address]) or not items:
        return Response({'error': 'Неверные данные'}, status=400)

    order = Order.objects.create(
        name=name,
        phone=phone,
        email=email,
        address=address,
    )

    for item in items:
        OrderItem.objects.create(
            order=order,
            product_id=item['product_id'],
            name=item['name'],
            price=item['price'],
            quantity=item['quantity']
        )

    return Response({'message': 'Заказ успешно оформлен!'})


@csrf_exempt
@require_POST
def update_cart(request, product_id):
    import json
    data = json.loads(request.body)
    action = data.get('action')

    cart = request.session.get('cart', {})

    if str(product_id) in cart:
        if action == 'increment':
            cart[str(product_id)]['quantity'] += 1
        elif action == 'decrement':
            cart[str(product_id)]['quantity'] -= 1
            if cart[str(product_id)]['quantity'] <= 0:
                del cart[str(product_id)]
    request.session['cart'] = cart
    request.session.modified = True

    return JsonResponse({'message': 'Корзина обновлена'})


@csrf_exempt
@require_POST
def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        request.session['cart'] = cart
        request.session.modified = True
    return JsonResponse({'message': 'Товар удалён из корзины'})

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


def remove_from_cart(request, product_id):
    cart = request.session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        del cart[product_id_str]
        request.session['cart'] = cart
        request.session.modified = True

    return redirect(request.META.get('HTTP_REFERER', 'cart'))


@csrf_exempt
@require_POST
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем корзину из сессии (если отсутствует, пустой словарь)
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

    # Логирование текущего состояния корзины
    print("КОРЗИНА ПОСЛЕ ДОБАВЛЕНИЯ:", cart)
    print("СЕССИЯ:", request.session.items())

    return JsonResponse({'message': 'Товар добавлен в корзину'}, status=200)


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

