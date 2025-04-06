import django_filters
from .models import Product, Category

class ProductFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name', lookup_expr='icontains', label='Название')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), label='Категория')
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte', label='Минимальная цена')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte', label='Максимальная цена')

    class Meta:
        model = Product
        fields = ['name', 'category', 'min_price', 'max_price']
