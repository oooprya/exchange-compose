from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.utils import timezone
from decimal import Decimal




class Currency(models.Model):
    name = models.CharField('Валюта', max_length=30, default='usd', unique = True)
    code = models.CharField(max_length=3)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        ordering = ('id',)
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"

    def save(self, *args, **kwargs):
        creating = not bool(self.id)
        result = super().save(*args, **kwargs)
        if creating:
            cache.delete(settings.CACHE_ALL_CURRENCY)
        return result


class Exchanger(models.Model):
    address = models.CharField(max_length=80)
    address_map = models.CharField(max_length=60, blank=True)
    working_hours = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updatedAt = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.address

    class Meta:
        ordering = ('id',)
        verbose_name = "Обменик"
        verbose_name_plural = "Все Обменики"

class CartItem(models.Model):

    exchanger = models.ForeignKey(Exchanger, on_delete=models.CASCADE)
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE)

    buy = models.DecimalField("Покупка", decimal_places=4, max_digits=10,  blank=True)
    sell = models.DecimalField("Продажа", decimal_places=4, max_digits=10, blank=True)
    
    sum = models.IntegerField("Остаток", default=100)

    updatedAt = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        
        if self.buy is not None:
            rounded_buy = self.buy.quantize(Decimal("0.001"))  # Округление
            self.buy = rounded_buy if rounded_buy * 1 != 0 else Decimal(int(rounded_buy))  # Убираем .00

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Курс валют"
        verbose_name_plural = "Курсы валют"

    def __str__(self) -> str:
        return f' Обменик: {self.exchanger.address} '

class Orders(models.Model):

    STATUS_CHOICES = (
    ('ordersent', 'Отправлен'),
    ('accepted', 'Принятый'),
    ('completed', 'Выполнен'),
    ('new', 'Новый'),
    ('cancel', 'Сancel'),
    )

    status = models.CharField(choices=STATUS_CHOICES, max_length=10, default='new')
    clients_telephone = models.CharField(max_length = 16, help_text='+38096-123-45-67')
    address_exchanger = models.CharField('Адрес Брони', max_length=100, blank=True)
    currency_name = models.CharField('Валюта', max_length=40, blank=True)
    buy_or_sell = models.CharField(max_length=8, blank=True)
    exchange_rate = models.DecimalField("Курс", decimal_places=2, max_digits=10, )
    order_sum = models.IntegerField("Сумма заказа", default=100)


    class Meta:
        ordering = ('-id',)
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
