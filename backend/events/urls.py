from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductListAPIView, CategoryViewSet
from .views import create_order
from .views import add_to_cart
from .views import get_cart

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('api/cart/add/<int:product_id>/', views.add_to_cart),
    path('cart/', views.view_cart, name='cart'),
    path('api/cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('api/cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/', include(router.urls)),
    path('api/products/', ProductListAPIView.as_view(), name='api-products'),
    path('api/cart/', views.get_cart),
    path('api/cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('api/cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('api/cart/place_order/', views.place_order, name='place_order'),
    path('api/orders/', create_order, name='create_order'),
]
