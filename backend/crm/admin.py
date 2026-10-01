from django.contrib import admin
from unfold.admin import ModelAdmin, TabularInline
from unfold.decorators import display

from .models import ClientProfile, ClientEvent


class ClientEventInline(TabularInline):
    model = ClientEvent
    extra = 0
    can_delete = False
    ordering = ("-created_at",)
   
    fields = (
    "event_type",
    "comment",
    "created_at",
    )

    readonly_fields = fields

    verbose_name = "Событие"
    verbose_name_plural = "📋 История клиента"

@admin.register(ClientProfile)
class ClientProfileAdmin(ModelAdmin):

    list_filter_sheet = True
    list_fullwidth = True
    list_per_page = 50

    list_display = (
        "phone",
        "client_name",
        "status_badge",
        "no_show_badge",
        "total_orders",
        "total_completed_orders",
        "last_visit",
    )
    inlines = [ClientEventInline]
    
    search_fields = (
        "phone",
        "first_name",
        "last_name",
    )

    list_filter = (
        "is_blacklisted",
        "created_at",
        "last_visit",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    ordering = ("-created_at",)

    fieldsets = (
        (
            "Основное",
            {
                "fields": (
                    "phone",
                    "first_name",
                    "last_name",
                    "telegram_id",
                )
            },
        ),
        (
            "Статус",
            {
                "fields": (
                    "is_blacklisted",
                    "blacklist_reason",
                    "no_show_count",
                )
            },
        ),
        (
            "Статистика",
            {
                "fields": (
                    "total_orders",
                    "total_completed_orders",
                    "last_visit",
                )
            },
        ),
        (
            "Комментарии",
            {
                "fields": (
                    "notes",
                )
            },
        ),
        (
            "Система",
            {
                "classes": ("collapse",),
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),
    )

    actions = (
        "blacklist_clients",
        "remove_blacklist",
    )

    @admin.action(description="🚫 Добавить в ЧС")
    def blacklist_clients(self, request, queryset):
        queryset.update(
            is_blacklisted=True
        )


    @admin.action(description="✅ Убрать из ЧС")
    def remove_blacklist(self, request, queryset):
        queryset.update(
            is_blacklisted=False,
            no_show_count=0
        )

    @display(description="Клиент")
    def client_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    @display(description="Статус", label=True)
    def status_badge(self, obj):

        if obj.is_blacklisted:
            return (
                "🔴 Чёрный список",
                "danger"
            )

        if obj.no_show_count >= 2:
            return (
                "🟡 Рискованный",
                "warning"
            )

        return (
            "🟢 Активный",
            "success"
        )
    
    
    @display(description="Неявки", label=True)
    def no_show_badge(self, obj):

        if obj.no_show_count >= 3:
            return (obj.no_show_count, "danger")

        if obj.no_show_count >= 2:
            return (obj.no_show_count, "warning")

        return (obj.no_show_count, "success")


@admin.register(ClientEvent)
class ClientEventAdmin(ModelAdmin):

    


    list_display = (
        "client",
        "event_badge",
        "created_at",
    )

    search_fields = (
        "client__phone",
        "comment",
    )

    list_filter = (
        "event_type",
        "created_at",
    )

    ordering = ("-created_at",)

    @display(description="Событие", label=True)
    def event_badge(self, obj):

        mapping = {
            "order_created": ("Бронь", "info"),
            "order_completed": ("Получил", "success"),
            "no_show": ("Не пришёл", "warning"),
            "blacklist": ("Блокировка", "danger"),
        }

        return mapping.get(
            obj.event_type,
            (obj.event_type, "primary")
        )
    
    