from django.contrib import admin
from django.utils.html import format_html

from .models import *

# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'get_price', 'get_image')

    @admin.display(description='Price')
    def get_price(self, obj):
        return obj.price

    @admin.display(description='Image')
    def get_image(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width: 50px; height: 50px;" />', obj.image.url)
        return "No Image"
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'complete', 'date_order')
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'get_price', 'quantity', 'date_added', 'get_total')

    @admin.display(description='Total Price')
    def get_total(self, obj):
        return obj.get_total

    @admin.display(description='Price')
    def get_price(self, obj):
        return obj.product.price if obj.product else 'N/A'



# admin.site.register(InformationCustomer)
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
