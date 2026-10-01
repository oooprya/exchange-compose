from django.db import models

class ClientTag(models.Model):
    name = models.CharField(max_length=50)

class ClientProfile(models.Model):
    phone = models.CharField(
        "Телефон",
        max_length=20,
        unique=True,
        db_index=True
    )

    first_name = models.CharField(
        "Имя клиента",
        max_length=100,
        blank=True
    )

    last_name = models.CharField(
        max_length=100,
        blank=True
    )

    tags = models.ManyToManyField(
        ClientTag,
        blank=True
    )

    telegram_id = models.CharField(
        max_length=50,
        blank=True
    )

    notes = models.TextField(
        "Комментарий",
        blank=True
    )

    is_blacklisted = models.BooleanField(
        default=False,
        verbose_name="Черный список"
    )

    blacklist_reason = models.TextField(
        blank=True
    )

    no_show_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Неявок"
    )

    # Статистика
    total_orders = models.PositiveIntegerField(
        default=0
    )

    total_completed_orders = models.PositiveIntegerField(
        default=0
    )

    last_visit = models.DateTimeField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.phone
    
    

class ClientEvent(models.Model):

    EVENT_TYPES = (
        ("order_created", "Создана бронь"),
        ("order_completed", "Получил валюту"),
        ("order_cancelled", "Отмена"),
        ("no_show", "Не пришёл"),
        ("blacklist", "В чёрный список"),
        ("whitelist", "Разблокирован"),
        ("comment", "Комментарий"),
    )

    client = models.ForeignKey(
        ClientProfile,
        on_delete=models.CASCADE,
        related_name="events"
    )

    event_type = models.CharField(
        max_length=30,
        choices=EVENT_TYPES
    )

    comment = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ("-created_at",)