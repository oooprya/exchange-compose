from django.urls import path
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.utils.html import format_html
from django.contrib import admin, messages
from django.utils.timezone import localtime
from decimal import Decimal, InvalidOperation
from django.shortcuts import redirect, render
from django.template.response import TemplateResponse

from unfold.admin import ModelAdmin, TabularInline, StackedInline

from currency.models import Currency
from wholesale.services.order_service import OrderService

from .models import (
    Shift,
    CashNode,
    StaffProfile,
    WholesaleOrder,
    CashBalance,
    CashMovement
)

# ─── Request-level cache helpers ─────────────────────────────────────────────

_STAFF_CACHE_KEY = "_cached_staff"
_SHIFT_CACHE_KEY = "_cached_shift"
_MISSING = object()


def get_staff(request):
    """Кэшируем staffprofile на весь request, чтобы не ходить в БД повторно."""
    if not hasattr(request, _STAFF_CACHE_KEY):
        setattr(request, _STAFF_CACHE_KEY, getattr(
            request.user, "staffprofile", None))
    return getattr(request, _STAFF_CACHE_KEY)


def get_open_shift(staff, request=None):
    """
    Возвращает открытую смену для сотрудника.
    Если передан request — кэшируем результат на уровне запроса,
    чтобы не делать повторные запросы к БД в рамках одного цикла обработки.
    """
    if request is not None:
        cached = getattr(request, _SHIFT_CACHE_KEY, _MISSING)
        if cached is not _MISSING:
            return cached

    result = _find_open_shift(staff)

    if request is not None:
        setattr(request, _SHIFT_CACHE_KEY, result)

    return result


def _find_open_shift(staff):
    """Только ищет открытую смену на сегодня. Не создаёт."""
    if not staff or not staff.is_active:
        return None

    today = timezone.localdate()

    return (
        Shift.objects
        .filter(staff=staff, is_open=True, opened_at__date=today)
        .select_related("node")
        .first()
    )


def _invalidate_shift_cache(request):
    """Сбрасывает кэш смены на request после создания/закрытия."""
    if hasattr(request, _SHIFT_CACHE_KEY):
        delattr(request, _SHIFT_CACHE_KEY)


class SomeInline(StackedInline):
    collapsible = True


class CashBalanceInline(TabularInline):
    model = CashBalance
    extra = 0
    # tab = True


@admin.register(CashNode)
class CashNodeAdmin(ModelAdmin):
    fields = ("node_type", "name", "exchange_point", "is_active")
    inlines = [CashBalanceInline]

    list_display = ("node_type", "name", "exchange_point", "is_active")


@admin.register(Shift)
class WholesaleShift(ModelAdmin):
    fields = ("staff", "node", "is_open")
    search_fields = ["staff"]
    list_display = ("staff", "node", "opened_at", "is_open")
    list_editable = ["is_open"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("staff", "node")

    def save_model(self, request, obj, form, change):
        staff = get_staff(request)
        obj.staff = staff
        obj.is_open = True
        super().save_model(request, obj, form, change)


@admin.register(StaffProfile)
class WholesaleStaffProfile(ModelAdmin):
    fields = ("role", "nodes", "user", "telephone", "is_active")


@admin.register(WholesaleOrder)
class WholesaleOrderAdmin(ModelAdmin):

    list_select_related = ("currency", "shift", "shift__node")
    change_list_template = "admin/wholesale/order_change_list.html"

    list_display = (
        "created_time",
        "currency",
        "order_type_badge",
        "amount_currency",
        "rate",
        "amount_base",
        "comment",
    )
    readonly_fields = ("created_at",)

    # ── permissions ──────────────────────────────────────────────────────────

    def has_add_permission(self, request):
        return get_open_shift(get_staff(request), request) is not None

    # ── queryset ─────────────────────────────────────────────────────────────

    def get_queryset(self, request):
        qs = (
            super()
            .get_queryset(request)
            .select_related("currency", "shift", "shift__node")
        )

        today = timezone.localdate()

        if request.user.is_superuser:
            return qs.filter(created_at__date=today)

        staff = get_staff(request)
        if not staff:
            return qs.none()

        if staff.role == "senior":
            return qs.filter(created_at__date=today)

        shift = get_open_shift(staff, request)
        if not shift:
            return qs.none()

        return qs.filter(shift=shift, created_at__date=today)

    # ── custom URLs ───────────────────────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "exchange/",
                self.admin_site.admin_view(self.exchange_view),
                name="wholesale_exchange",
            ),
            path(
                "get-balance/",
                self.admin_site.admin_view(self.get_balance_view),
                name="wholesale_get_balance",
            ),
            path(
                "select-node/",
                self.admin_site.admin_view(self.select_node_view),
                name="wholesale_select_node",
            ),
        ]
        return custom + urls

    # ── select node & open shift ──────────────────────────────────────────────

    def select_node_view(self, request):
        """
        POST: получаем node_id, открываем смену на выбранную кассу.
        Единственное место где создаётся смена.
        """
        if request.method != "POST":
            return JsonResponse({"success": False, "error": "Метод не поддерживается"}, status=405)

        staff = get_staff(request)
        if not staff or not staff.is_active:
            return JsonResponse({"success": False, "error": "Профиль не найден"}, status=403)

        node_id = request.POST.get("node_id")
        if not node_id:
            return JsonResponse({"success": False, "error": "Касса не выбрана"}, status=400)

        # Проверяем что касса принадлежит этому сотруднику
        node = staff.nodes.filter(pk=node_id, is_active=True).first()
        if not node:
            return JsonResponse({"success": False, "error": "Касса недоступна"}, status=403)

        # Закрываем старые открытые смены одним UPDATE
        Shift.objects.filter(staff=staff, is_open=True).update(
            is_open=False,
            closed_at=timezone.now(),
        )

        # Создаём новую смену на выбранную кассу
        shift = Shift.objects.create(
            staff=staff,
            node=node,
            is_open=True,
            opened_at=timezone.now(),
        )

        _invalidate_shift_cache(request)

        return JsonResponse({"success": True, "shift_id": shift.pk, "node_name": node.name})

    # ── changelist ────────────────────────────────────────────────────────────

    def changelist_view(self, request, extra_context=None):
        staff = get_staff(request)
        shift = None
        balances = None
        available_nodes = []
        needs_node_selection = False

        if staff and staff.is_active:
            shift = get_open_shift(staff, request)
            available_nodes = list(staff.nodes.filter(is_active=True))

            if shift:
                balances = (
                    CashBalance.objects
                    .filter(node=shift.node, balance__gt=0)
                    .select_related("currency")
                )
            else:
                # Смены нет — показываем выбор кассы если есть доступные
                needs_node_selection = len(available_nodes) > 0
                print(f'needs_node_selection {needs_node_selection}')

        extra_context = extra_context or {}
        extra_context["current_shift"] = shift
        extra_context["current_balances"] = balances
        extra_context["available_nodes"] = available_nodes
        extra_context["needs_node_selection"] = needs_node_selection
        # Одна касса — JS откроет смену автоматически без показа списка
        extra_context["auto_select_node"] = (
            needs_node_selection and len(available_nodes) == 1
        )

        return super().changelist_view(request, extra_context=extra_context)

    # ── form helpers ──────────────────────────────────────────────────────────

    def get_changeform_initial_data(self, request):
        initial = super().get_changeform_initial_data(request)
        order_type = request.GET.get("order_type")
        shift_id = request.GET.get("shift")
        if order_type:
            initial["order_type"] = order_type
        if shift_id:
            initial["shift"] = shift_id
        return initial

    def get_fieldsets(self, request, obj=None):
        if request.GET.get("order_type") in ["in", "out"]:
            return (
                (None, {"fields": ("shift", "currency",
                 "order_type", "amount_currency", "comment")}),
            )
        return (
            (None, {"fields": (
                "shift", "currency", "order_type",
                "amount_currency", "rate", "amount_base",
                "old_currency", "comment",
            )}),
        )

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if "shift" in form.base_fields:
            form.base_fields["shift"].disabled = True
        return form

    # ── display helpers ──────────────────────────────────────────────────────

    def created_time(self, obj):
        if obj.created_at:
            return localtime(obj.created_at).strftime("%H:%M:%S")
        return "-"

    created_time.short_description = "Час"
    created_time.admin_order_field = "created_at"

    def order_type_badge(self, obj):
        colors = {
            "buy": "bg-green-100 text-green-700",
            "sell": "bg-blue-100 text-blue-700",
            "in": "bg-emerald-100 text-emerald-700",
            "out": "bg-red-100 text-red-700",
        }
        labels = dict(obj.ORDER_TYPES)
        return format_html(
            '<span class="px-2 py-1 rounded text-xs font-semibold {}">{}</span>',
            colors.get(obj.order_type, "bg-gray-100"),
            labels.get(obj.order_type),
        )

    order_type_badge.short_description = "Тип"

    # ── API views ─────────────────────────────────────────────────────────────

    def get_balance_view(self, request):
        staff = get_staff(request)
        shift = get_open_shift(staff, request)

        if not shift:
            return JsonResponse({"balance": 0})

        currency_id = request.GET.get("currency")
        if not currency_id:
            return JsonResponse({"balance": 0})

        balance = (
            CashBalance.objects
            .filter(node=shift.node, currency_id=currency_id)
            .values_list("balance", flat=True)
            .first()
        )
        return JsonResponse({"balance": float(balance or 0)})

    def exchange_view(self, request):
        staff = get_staff(request)
        shift = get_open_shift(staff, request)

        if not shift:
            messages.error(request, "Смена не открыта")
            return redirect("..")

        order_type = request.GET.get("type", "buy")
        if order_type not in {"buy", "sell", "in", "out"}:
            order_type = "buy"

        if request.method == "POST":
            try:
                currency = Currency.objects.get(
                    id=request.POST.get("currency"))
                amount = Decimal(request.POST.get("amount"))
            except (Currency.DoesNotExist, InvalidOperation, TypeError):
                messages.error(request, "Ошибка данных")
                return redirect(request.path)

            rate = None
            if order_type in {"buy", "sell"}:
                try:
                    rate = Decimal(request.POST.get("rate"))
                except (InvalidOperation, TypeError):
                    messages.error(request, "Некорректный курс")
                    return redirect(request.path)

            try:
                OrderService.create_order(
                    shift=shift,
                    currency=currency,
                    order_type=order_type,
                    amount_currency=amount,
                    rate=rate,
                    comment=request.POST.get("comment", ""),
                )
                messages.success(request, "Операция проведена")
            except Exception as e:
                messages.error(request, str(e))

            return redirect("..")

        # ── GET: строим queryset валют одним запросом ────────────────────────
        currencies = Currency.objects.all()

        if order_type in {"buy", "sell"}:
            currencies = currencies.exclude(code="uah")

        if order_type == "sell":
            # Подзапрос вместо двух отдельных запросов
            available_ids = (
                CashBalance.objects
                .filter(node=shift.node, balance__gt=0)
                .values_list("currency_id", flat=True)
            )
            currencies = currencies.filter(id__in=available_ids)

        context = {
            **self.admin_site.each_context(request),
            "currencies": currencies,
            "order_type": order_type,
            "is_movement": order_type in {"in", "out"},
            "current_shift": shift,
        }

        return TemplateResponse(
            request,
            "admin/wholesale/exchange_form.html",
            context,
        )


# ─── CashBalance ──────────────────────────────────────────────────────────────

@admin.register(CashBalance)
class CashBalanceAdmin(ModelAdmin):
    list_display = ("node", "currency", "balance")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("node", "currency")


# ─── CashMovement ─────────────────────────────────────────────────────────────

@admin.register(CashMovement)
class CashMovementAdmin(ModelAdmin):
    list_display = ("node", "currency", "movement_badge",
                    "amount", "comment", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("node", "currency")

    def movement_badge(self, obj):
        if obj.movement_type == "in":
            return format_html('<span style="color:#16a34a">⬆ In</span>')
        elif obj.movement_type == "buy":
            return format_html('<span style="color:#16a34a">⬇ Покупка</span>')
        return format_html('<span style="color:#dc2626">⬇ Out</span>')
