from django.urls import path
from django.utils import timezone
from datetime import timedelta, datetime, time
from django.http import JsonResponse, HttpResponseRedirect

from django.utils.html import format_html
from django.contrib import admin, messages
from django.utils.timezone import localtime
from decimal import Decimal, InvalidOperation
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.db import transaction
from django.template.response import TemplateResponse

from django.db.models import Case, When, Value, BooleanField

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
    show_full_result_count = False

    list_select_related = ("currency", "shift", "shift__node")
    change_list_template = "admin/wholesale/order_change_list.html"

    list_display = (
        "created_time",
        "currency",
        "order_type_badge",
        "amount_currency",
        "rate",
        "amount_base",
        "reverse_action",
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

        qs = qs.annotate(
            can_reverse=Case(
                When(
                    created_at__gte=timezone.now() - timedelta(minutes=30),
                    is_reversed=False,
                    then=Value(True)
                ),
                default=Value(False),
                output_field=BooleanField()
            )
        )

        node_id = request.GET.get("shift__node__id")

        if node_id:
            if str(node_id).isdigit():
                node_id = int(node_id)
            else:
                node_id = None

        if request.user.is_superuser:
            if node_id:
                return qs.filter(shift__node_id=node_id, created_at__date=today)

            return qs.filter(created_at__date=today)

        staff = get_staff(request)
        if not staff:
            return qs.none()

        if staff.role == "senior":

            if node_id:
                return qs.filter(
                    shift__node_id=node_id,
                    created_at__date=today
                )

            return qs.none()

        # Обычный кассир — только своя смена
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
            path(
                "reverse/<int:order_id>/",
                self.admin_site.admin_view(self.reverse_order_view),
                name="reverse_order",
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

        today = timezone.localdate()

        start = timezone.make_aware(datetime.combine(today, time.min))
        end = timezone.make_aware(datetime.combine(today, time.max))

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

    def lookup_allowed(self, lookup, value):

        if lookup == 'shift__node__id':
            return True
        return super().lookup_allowed(lookup, value)

    # ── changelist ────────────────────────────────────────────────────────────

    def changelist_view(self, request, extra_context=None):
        staff = get_staff(request)
        shift = None
        balances = None
        available_nodes = []
        needs_node_selection = False
        all_nodes = []
        selected_node = None

        node_id = request.GET.get("shift__node__id")

        is_senior = (
            request.user.is_superuser or
            (staff and staff.role == "senior")
        )

        if staff and staff.is_active:
            shift = get_open_shift(staff, request)
            available_nodes = list(staff.nodes.filter(is_active=True))

            if not is_senior:
                if shift:
                    balances = (
                        CashBalance.objects
                        .filter(node=shift.node, balance__gt=0)
                        .select_related("currency")
                    )
                else:
                    needs_node_selection = len(available_nodes) > 0

        if is_senior:
            today = timezone.localdate()

            nodes_with_open_shift = set(
                Shift.objects
                .filter(is_open=True, opened_at__date=today)
                .values_list("node_id", flat=True)
            )

            all_nodes = list(
                CashNode.objects
                .filter(pk__in=nodes_with_open_shift, is_active=True)
                .order_by("pk")
            )

            request.selected_node_id = node_id

            node_id = getattr(request, "selected_node_id", None)
            if node_id:
                try:
                    node_id = int(node_id)
                    selected_node = next(
                        (n for n in all_nodes if n.pk == node_id),
                        None
                    )
                except ValueError:
                    selected_node = None

            if not selected_node and all_nodes:
                selected_node = all_nodes[0]

            if not node_id and selected_node and all_nodes:
                return HttpResponseRedirect(f"?shift__node__id={selected_node.pk}")

            balances = (
                CashBalance.objects
                .filter(node=selected_node, balance__gt=0)
                .select_related("currency")
            ) if selected_node else None

        extra_context = extra_context or {}
        extra_context["current_shift"] = shift
        extra_context["current_balances"] = balances
        extra_context["available_nodes"] = available_nodes
        extra_context["needs_node_selection"] = needs_node_selection
        extra_context["auto_select_node"] = (
            needs_node_selection and len(available_nodes) == 1
        )
        extra_context["all_nodes"] = all_nodes
        extra_context["selected_node"] = selected_node
        # ← Ключевое: если нет ?node= передаём pk первой кассы
        # чтобы Django правильно рендерил активный класс без JS
        extra_context["selected_node_id"] = selected_node.pk if selected_node else None
        extra_context["is_senior"] = is_senior

        return super().changelist_view(request, extra_context=extra_context)

    @transaction.atomic
    def reverse_order_view(self, request, order_id):
        order = get_object_or_404(
            WholesaleOrder.objects.select_for_update(),
            pk=order_id
        )

        if order.is_reversed:
            messages.error(request, "Операция уже сторнирована")
            return redirect("admin:wholesale_wholesaleorder_changelist")

        if order.created_at < timezone.now() - timedelta(minutes=30):
            messages.error(request, "Прошло более 30 минут")
            return redirect("admin:wholesale_wholesaleorder_changelist")

        # last_order = WholesaleOrder.objects.order_by("-created_at").first()
        # if last_order and last_order.id != order.id:
        #     messages.error(
        #         request, "Можно сторнировать только последнюю операцию")
        #     return redirect("admin:wholesale_wholesaleorder_changelist")

        try:
            # 🔁 Определяем обратный тип
            reverse_type = {
                "buy": "sell",
                "sell": "buy",
                "in": "out",
                "out": "in",
            }[order.order_type]

            # 🔁 Создаём обратный ордер
            reverse_order = OrderService.create_order(
                shift=order.shift,
                currency=order.currency,
                order_type=reverse_type,
                amount_currency=order.amount_currency,
                rate=order.rate,
                amount_base=order.amount_base,
                base_currency=order.base_currency,
                comment=(
                    f"СТОРНО #{order.id} | "
                    f"{order.get_order_type_display()} {order.amount_currency} {order.currency.code}"
                    + (
                        f" ({order.base_currency.code})" if order.base_currency else ""
                    )
                ),
            )

            order.is_reversed = True
            order.save(update_fields=["is_reversed"])

            messages.success(
                request, f"Сторно выполнено (#{reverse_order.id})")

        except Exception as e:
            messages.error(request, f"Ошибка сторно: {str(e)}")

        return redirect("admin:wholesale_wholesaleorder_changelist")

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
                "is_reversed", "comment",
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
        # Для сторно показываем отдельный красный бейдж, чтобы не путать с обычными типами
        if obj.is_reversed or (obj.comment and obj.comment.startswith("Сторно #")):
            return format_html(
                '<span class="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-700">Сторно</span>'
            )

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

    def reverse_action(self, obj):
        is_reversal = obj.comment and obj.comment.startswith("Сторно #")

        if obj.can_reverse and not obj.is_reversed and not is_reversal:
            url = reverse("admin:reverse_order", args=[obj.id])
            return format_html(
                '<a href="{}" onclick="return confirm(\'Отменить заказ?\')" '
                'class="px-2 py-1 rounded text-xs font-semibold bg-red-100 text-red-700 hover:text-green-700" title="Отменить заказ">✖︎</a>',
                url
            )
        if obj.is_reversed:
            return "✓"
        else:
            return ""

    reverse_action.short_description = ""

    # ── API views ─────────────────────────────────────────────────────────────

    def get_balance_view(self, request):
        staff = get_staff(request)
        shift = get_open_shift(staff, request)

        if not shift:
            return JsonResponse({"balance": 0})

        currency_id = request.GET.get("currency")
        currency_code = request.GET.get("currency_code")
        order_type = request.GET.get("order_type", "buy")

        if not currency_id:
            return JsonResponse({"balance": 0})

        # Если это кроссовый курс, получаем баланс нужной валюты
        if currency_code and '-' in currency_code:
            parts = currency_code.split('-')
            base_code = parts[0]
            quote_code = parts[1]

            try:
                if order_type == "sell":
                    # При продаже: показываем баланс quote валюты (EUR)
                    target_currency = Currency.objects.get(code=quote_code)
                    currency_id = target_currency.id
                else:
                    base_currency_id = request.GET.get("base_currency_id")

                    if base_currency_id:
                        target_currency = Currency.objects.get(
                            id=base_currency_id)
                    else:
                        target_currency = Currency.objects.filter(
                            code=base_code).first()

                currency_id = target_currency.id
            except Currency.DoesNotExist:
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
            amount_base = None
            base_currency = None

            # Определяем тип курса по коду валюты
            is_cross_rate = currency.code and '-' in currency.code

            if is_cross_rate:
                # Получаем выбранную версию базовой валюты (USD, USD-new и т.д.)
                base_currency_id = request.POST.get("base_currency")
                if base_currency_id:
                    try:
                        base_currency = Currency.objects.get(
                            id=base_currency_id)
                    except Currency.DoesNotExist:
                        messages.error(request, "Версія валюти не знайдена")
                        return redirect(request.path)

                try:
                    rate = Decimal(request.POST.get("rate"))
                    amount_base = amount * rate

                except (InvalidOperation, TypeError):
                    messages.error(
                        request, "Некорректна сума у базовій валюті")
                    return redirect(request.path)
            else:
                # Обычный курс
                if order_type in {"buy", "sell"}:
                    try:
                        rate = Decimal(request.POST.get("rate"))
                        amount_base = amount * rate
                    except (InvalidOperation, TypeError):
                        messages.error(request, "Некорректный курс")
                        return redirect(request.path)
                else:
                    # Для "in"/"out" - amount_base = amount
                    amount_base = amount

            try:
                # Если это крос-курс, передаем выбранную базовую валюту
                if base_currency and is_cross_rate:
                    OrderService.create_order(
                        shift=shift,
                        currency=currency,
                        order_type=order_type,
                        amount_currency=amount,
                        rate=rate,
                        amount_base=amount_base,
                        comment=request.POST.get("comment", ""),
                        base_currency=base_currency,
                    )
                else:
                    OrderService.create_order(
                        shift=shift,
                        currency=currency,
                        order_type=order_type,
                        amount_currency=amount,
                        rate=rate,
                        amount_base=amount_base,
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

            # Получаем доступные балансы на кассе
            available_currency_ids = set(
                CashBalance.objects
                .filter(node=shift.node, balance__gt=0)
                .values_list("currency_id", flat=True)
            )
            available_codes = list(
                CashBalance.objects
                .filter(node=shift.node, balance__gt=0)
                .select_related("currency")
                .values_list("currency__code", flat=True)
            )

            available_ids = list(available_currency_ids)

            # Проверяем крос-курсы
            all_currencies = Currency.objects.all()
            for curr in all_currencies:
                if curr.code and '-' in curr.code:
                    parts = curr.code.split('-')

                    if parts[0] == "usd":
                        base_code = parts[0]
                        quote_code = parts[1]
                    elif parts[1] == "usd":
                        base_code = parts[1]
                        quote_code = parts[0]

                    print(f'base_code {base_code}')

                    has_quote = quote_code in available_codes
                    has_base = any(code == base_code or code.startswith(base_code + '-')
                                   for code in available_codes)

                    print(f'has_base {has_base}')

                    if order_type == "buy":
                        # Для покупки EUR-USD: нужна базовая валюта USD (линосн платим)
                        if has_base:
                            available_ids.append(curr.id)
                    elif order_type == "sell":
                        # Для продажи EUR-USD: нужна quote валюта EUR (то, что продаем)
                        if has_quote:
                            available_ids.append(curr.id)
        if order_type == "sell":
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
        qs = super().get_queryset(request).select_related("node", "currency")

        # Superusers can see all balances.
        if request.user.is_superuser:
            return qs

        staff = get_staff(request)
        if not staff:
            return qs.none()

        allowed_nodes = staff.nodes.filter(
            is_active=True).values_list("id", flat=True)
        return qs.filter(node_id__in=allowed_nodes)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # Ограничиваем выбор касс только теми, которые есть у сотрудника
        if db_field.name == "node" and not request.user.is_superuser:
            staff = get_staff(request)
            if staff:
                kwargs["queryset"] = staff.nodes.filter(is_active=True)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# ─── CashMovement ─────────────────────────────────────────────────────────────

@admin.register(CashMovement)
class CashMovementAdmin(ModelAdmin):
    list_display = ("node", "currency", "movement_badge",
                    "amount", "comment", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("node", "currency")

    def movement_badge(self, obj):
        # Показываем направление движения для данной валюты.
        # - buy: валюта приходит в кассу (⬆)
        # - sell: валюта уходит из кассы (⬇)
        if obj.movement_type == "in":
            return format_html('<span style="color:#16a34a">⬆ In</span>')
        elif obj.movement_type == "buy":
            return format_html('<span class="px-2 py-1 rounded text-xs bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400">⬆ Покупка</span>')
        elif obj.movement_type == "sell":
            return format_html('<span class="px-2 py-1 rounded text-xs bg-blue-100 text-blue-700">⬇ Продажа</span>')
        return format_html('<span style="color:#dc2626">⬇ Out</span>')
