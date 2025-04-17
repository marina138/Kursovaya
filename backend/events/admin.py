# events/admin.py

from django.contrib import admin
from .models import Product, Category, Order
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'created_at')
    inlines = [OrderItemInline]


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'category', 'preview_image')
    readonly_fields = ['preview_image']

    def preview_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-height: 100px;" />', obj.image.url)
        return "-"
    preview_image.short_description = "Image"

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
