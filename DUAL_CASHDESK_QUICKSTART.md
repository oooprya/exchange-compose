# 🚀 Быстрый старт: Система двух касс

## Что было добавлено?

✅ **Новый интерфейс** в order_change_list.html с управлением двумя кассами  
✅ **Модальное окно** для перевода денег между кассой и сейфом  
✅ **API endpoint** для безопасной обработки переводов  
✅ **Отслеживание операций** через CashMovement  

## 1️⃣ Быстрая настройка (5 минут)

### Шаг 1: Создать две кассы (если не созданы)

```bash
# В Django shell:
python manage.py shell

from wholesale.models import CashNode
from currency.models import Exchanger

# Найти вашу точку обмена
exchange_point = Exchanger.objects.first()  # или нужную точку

# Создать кассу и сейф
desk = CashNode.objects.create(
    name="Касса",
    exchange_point=exchange_point,
    node_type="desk",
    is_active=True
)

safe = CashNode.objects.create(
    name="Сейф",
    exchange_point=exchange_point,
    node_type="safe",
    is_active=True
)

print(f"✅ Касса создана: {desk}")
print(f"✅ Сейф создан: {safe}")
```

### Шаг 2: Инициализировать балансы

```python
from currency.models import Currency
from wholesale.models import CashBalance

# Получить все валюты
currencies = Currency.objects.all()

# Создать балансы для кассы
for currency in currencies:
    CashBalance.objects.get_or_create(
        node=desk,
        currency=currency,
        defaults={"balance": 0}
    )

# Создать балансы для сейфа
for currency in currencies:
    CashBalance.objects.get_or_create(
        node=safe,
        currency=currency,
        defaults={"balance": 0}
    )

print(f"✅ Балансы инициализированы")
```

### Шаг 3: Проверить в админке

1. Откройте `/admin/wholesale/cashnode/`
2. Убедитесь что видите обе кассы (Касса и Сейф)
3. Откройте `/admin/wholesale/wholesaleorder/` 
4. Справа должна быть панель **"💰 Кассы"** с вкладками

## 2️⃣ Как это работает?

### Панель баланса (справа на странице заказов)

```
💰 Кассы
┌──────────────────┐
│ 🏪 | 🔐 | ⚖️ | 📅 │  ← Четыре вкладки
├──────────────────┤
│                  │
│  USD    1000.00  │  ← Баланс по валютам
│  EUR     500.00  │
│  UAH   50000.00  │
│                  │
│ [💸 Перевести]   │  ← Кнопка на вкладке "Итого"
└──────────────────┘
```

### Процесс перевода

```
1. Выберите "⚖️ Итого" вкладку
2. Нажмите "💸 Перевести между кассами"
3. Заполните форму:
   - Откуда: Касса
   - Куда: Сейф
   - Валюта: USD
   - Сумма: 1000
4. Нажмите "Перевести"
5. ✅ Балансы обновлены автоматически!
```

## 3️⃣ Примеры команд

### Проверить текущие балансы

```python
from wholesale.models import CashNode, CashBalance

desk = CashNode.objects.get(node_type="desk")
safe = CashNode.objects.get(node_type="safe")

print("Касса:")
for b in desk.balances.all():
    print(f"  {b.currency.code}: {b.balance}")

print("\nСейф:")
for b in safe.balances.all():
    print(f"  {b.currency.code}: {b.balance}")
```

### История переводов

```python
from wholesale.models import CashMovement
from django.utils import timezone
from datetime import timedelta

# Переводы за последний час
hour_ago = timezone.now() - timedelta(hours=1)
transfers = CashMovement.objects.filter(
    created_at__gte=hour_ago,
    movement_type__in=['in', 'out']
).order_by('-created_at')

for move in transfers:
    print(f"{move.created_at} | {move.node} | {move.currency} | {move.amount} | {move.movement_type}")
```

## 4️⃣ Что происходит при переводе?

```
Перевод 1000 USD из Кассы в Сейф:

1. Кассирать вводит данные в модальном окне
2. JavaScript отправляет POST запрос на:
   /admin/wholesale/transfer-between-desks/

3. Backend обрабатывает:
   ✓ Проверяет наличие достаточных средств
   ✓ Уменьшает баланс Кассы на 1000 USD
   ✓ Увеличивает баланс Сейфа на 1000 USD
   ✓ Создает CashMovement записи

4. Клиент получает:
   {
     "success": true,
     "message": "Успешно переведено 1000.00 USD..."
   }

5. Страница перезагружается - балансы обновлены!
```

## 5️⃣ Ошибки и решения

### Ошибка: "Кассы не найдены"
**Решение:** Создайте CashNode'ы с правильными типами (desk, safe)

### Ошибка: "Недостаточно USD"
**Решение:** В кассе/сейфе недостаточно денег, проверьте баланс

### Ошибка: "CSRF токен не валидален"
**Решение:** Перезагрузите страницу, CSRF токен должен быть в форме

### Панель баланса не показывает две кассы
**Решение:** 
1. Убедитесь что у кассира есть доступ к обеим кассам (StaffProfile.nodes)
2. Проверьте что на одной точке обмена две разные кассы (desk и safe)
3. Очистите браузерный кэш

## 6️⃣ Интеграция с существующей системой

Система полностью интегрирована с существующей логикой:

- ✅ Используются существующие модели (CashNode, CashBalance, CashMovement)
- ✅ Работает с текущей системой смен (Shift)
- ✅ Совместима с операциями покупки/продажи
- ✅ Отслеживается в истории операций
- ✅ Влияет на финансовый результат смены

## 📂 Измененные файлы

```
backend/wholesale/admin.py
  + transfer_between_desks_view() метод
  + новый URL path

backend/templates/admin/wholesale/order_change_list.html
  + Новая панель баланса с двумя кассами
  + Модальное окно для переводов
  + JavaScript логика управления
```

## 🎓 Дополнительно

Для подробной документации смотрите [DUAL_CASHDESK_GUIDE.md](./DUAL_CASHDESK_GUIDE.md)
