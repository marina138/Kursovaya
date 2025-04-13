from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from .views import ProductListAPIView, CategoryViewSet

router = DefaultRouter()
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog_view, name='catalog'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='cart'),
    path('remove_from_cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/increase/<int:product_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:product_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('checkout/', views.checkout, name='checkout'),
    path('api/', include(router.urls)),
    path('api/products/', ProductListAPIView.as_view(), name='api-products'),
]
