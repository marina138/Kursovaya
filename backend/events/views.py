from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_POST
from rest_framework.generics import ListAPIView
from rest_framework import generics, viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
from .models import Product, Category, Order, OrderItem, Customer, Cart, CartItem
from .filters import ProductFilter
from .forms import AddToCartForm
from .serializers import ProductSerializer, OrderSerializer, CategorySerializer
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from decimal import Decimal
from django.core.exceptions import ValidationError
import logging

logger = logging.getLogger(__name__)

# Эндпоинт для получения CSRF-токена
@ensure_csrf_cookie
def get_csrf_token(request):
    logger.info("Запрос на получение CSRF-токена")
    return JsonResponse({'csrfToken': request.META.get('CSRF_TOKEN', '')})

@api_view(['POST'])
def create_order(request):
    logger.info(f"Получен POST-запрос на /api/order/: {request.data}")
    logger.info(f"Заголовки запроса: {request.headers}")

    data = request.data
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    address = data.get('address')
    items = data.get('items', [])

    if not all([name, phone, email, address]) or not items:
        logger.error(f"Неверные данные: name={name}, phone={phone}, email={email}, address={address}, items={items}")
        return Response({'error': 'Все поля обязательны и корзина не должна быть пуста'}, status=400)

    try:
        order = Order.objects.create(
            name=name,
            phone=phone,
            email=email,
            address=address,
        )
        logger.info(f"Создан заказ: {order.id}")

        for item in items:
            OrderItem.objects.create(
                order=order,
                product_id=item['product_id'],
                name=item['name'],
                price=item['price'],
                quantity=item['quantity']
            )
        logger.info(f"Добавлены товары к заказу: {order.id}")

        return Response({'message': 'Заказ успешно оформлен!'}, status=201)
    except Exception as e:
        logger.error(f"Ошибка при создании заказа: {str(e)}")
        return Response({'error': f'Ошибка сервера: {str(e)}'}, status=500)

# Остальные функции остаются без изменений
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

        logger.info(f"Полученные данные для place_order: {data}")

        customer, created = Customer.objects.get_or_create(
            phone=phone,
            defaults={'phone': phone, 'email': email}
        )
        if not created and email and customer.email != email:
            customer.email = email
            customer.save()

        order = Order(address="Адрес по умолчанию")
        try:
            order.full_clean()
            order.save()
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)

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

        if 'cart' in request.session:
            del request.session['cart']
            request.session.modified = True

        return JsonResponse({'message': 'Заказ успешно оформлен!'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Некорректный формат JSON'}, status=400)
    except Exception as e:
        logger.error(f"Ошибка в place_order: {str(e)}")
        return JsonResponse({'error': f'Ошибка сервера: {str(e)}'}, status=500)

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
    products = product_filter.qs
    return render(request, 'catalog.html', {
        'filter': product_filter,
        'products': products
    })

@csrf_exempt
@require_POST
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

    logger.info(f"КОРЗИНА ПОСЛЕ ДОБАВЛЕНИЯ: {cart}")
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

        request.session['cart'] = {}
        request.session.modified = True

        return render(request, 'checkout.html', {'message': 'Заказ оформлен'})
    return render(request, 'checkout.html')