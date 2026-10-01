from decimal import Decimal

CURRENCY_TEMPLATES = {
    'usd': ("🇺🇸 🇺🇦 <b>USD {buy} / {sell}</b> білий\n", 1),
    'usdnew': ("🇺🇸 🇺🇦 <b>USD {buy} / {sell}</b> синій 💙\n", 2),
    'eur': ("🇪🇺 🇺🇦 <b>EUR {buy} / {sell}</b>\n\n💱Крос - курс:\n", 3),
    'usd-eur': ("🇺🇸 🇪🇺 $/€ {buy} / {sell}\n", 3),
    'chf-usd': ("🇺🇸 🇨🇭 $/₣ {buy} / {sell}\n", 4),
    'gbp-usd': ("🇺🇸 🇬🇧 $/£ {buy} / {sell}\n\n🔻 Інші валюти:\n", 5),
    'gbp': ("🇬🇧 🇺🇦 GBP: {buy} / {sell}\n", 5),
    'chf': ("🇨🇭 🇺🇦 CHF: {buy} / {sell}\n", 6),
    'pln': ("🇵🇱 🇺🇦 PLN: {buy} / {sell}\n", 6),
    'ron': ("🇷🇴 🇺🇦 RON: {buy} / {sell}\n", 7),
    'mdl': ("🇲🇩 🇺🇦 MLD: {buy} / {sell}\n", 8),
    'cad': ("🇨🇦 🇺🇦 CAD: {buy} / {sell}\n", 12),
    'nok': ("🇳🇴 🇺🇦 NOK: {buy} / {sell}\n", 13),
}

EXCHANGER_NOVYI_RYNOK = "4"

DISCOUNT_USD_NEW = Decimal("0.20")
DISCOUNT_USD = Decimal("0.20")
DISCOUNT_EUR = Decimal("0.25")



ORDER_STATUS = {
    "new": {
        "label": "✉️ Надіслано",
        "client_text": """
📝 Заявку №{id} отримано

Ваше бронювання передано оператору на обробку.

⏳ Очікуйте підтвердження.
"""
    },

    "accepted": {
        "label": "✅ Підтверджено",
        "client_text": """
✅ Бронювання №{id} підтверджено

💱 Валюта: {currency}
💵 Сума: <b> {amount}</b> 
📍 Пункт обміну: {address}

📌 Курс зафіксовано: <b> {rate}</b> 

⏰ Бронювання дійсне 90 хвилин.
"""
    },

    "completed": {
        "label": "🎉 Виконано",
        "client_text": """
🎉 Обмін успішно завершено

Номер бронювання: {id}

Дякуємо за довіру ❤️
"""
    },

    "cancel": {
        "label": "❌ Скасовано",
        "client_text": """
❌ Бронювання №{id} скасовано.

Ви можете створити нову заявку за актуальним курсом.
"""
    },

    "noshow": {
        "label": "⚠️ Неявка",
        "client_text": """
⚠️ Бронювання №{id} закрито.

Ви не звернулися до пункту обміну протягом часу дії бронювання.
"""
    }
}