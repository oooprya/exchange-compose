from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import Exchanger, Currency, CartItem, Orders

class CurrencyInline(admin.TabularInline):
    model = CartItem
    extra = 1

class ExchangerInline(admin.TabularInline):
    model = Exchanger
    extra = 1

class CartItemAdmin(ModelAdmin):
    list_display = ("id", "exchanger", "exchanger_id", "currency", 'buy', 'sell', 'sum')
    list_editable = ('buy', 'sell', 'sum')
    list_display_links = ["exchanger"]

class CurrencyAdmin(ModelAdmin):
    list_display = ["name", "code"]


class ExchangerAdmin(ModelAdmin):
    inlines = [CurrencyInline]
    list_display = ["id","address"]
    list_display_links = ["address"]

class OrdersAdmin(ModelAdmin):
    list_display = ("id", 'currency_name', 'buy_or_sell', 'order_sum','exchange_rate', "status", "address_exchanger")
    list_editable = ['status']


admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Currency, CurrencyAdmin)
admin.site.register(Orders, OrdersAdmin)
admin.site.register(Exchanger, ExchangerAdmin)

# Register your models here.
