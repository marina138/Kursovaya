from rest_framework import serializers
from .models import Product
from .models import Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer()  # ← включаем категорию

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'image', 'category']