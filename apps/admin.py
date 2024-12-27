from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Product)
admin.site.register(Order)
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'order', 'quantity', 'date_added')
    list_per_page = 200

# admin.site.register(InformationCustomer)
admin.site.register(Category)
