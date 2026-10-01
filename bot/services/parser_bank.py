import hashlib
import asyncio
import aiohttp
from loguru import logger
import aiosqlite
from datetime import datetime
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

logger.add("Logs.log", colorize=True,
           format="{time:YYYY-MM-DD HH:mm:ss} {name} {line} {level} {message} ", level="DEBUG", rotation="500 KB", compression="zip")
# from config import TELEGRAM_CHAT_ID, TELEGRAM_TOKEN

# ==============================
# CONFIG
# ==============================

URL = "https://kurs.com.ua/ru/gorod/1551-odessa#organizations_table_cash_bank"
DB_NAME = "rates.db"


THRESHOLD = 0.03
TELEGRAM_TOKEN = '8097135106:AAEx1pM7yX-Z_T3poJi_BgOVeXD9dYgVvR0'
TELEGRAM_CHAT_ID = '-1003588851573'

# ==============================
# DATABASE
# ==============================

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS bank_rates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TEXT NOT NULL,
    bank_name TEXT NOT NULL,
    bank_url TEXT NOT NULL,
    buy REAL NOT NULL,
    sell REAL NOT NULL,
    bank_update TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sent_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    message_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
"""


def hash_message(text: str) -> str:
    if not isinstance(text, str):
        raise TypeError(f"Expected str, got {type(text)}")

    return hashlib.sha256(text.encode()).hexdigest()


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(CREATE_TABLE_SQL)
        await db.commit()


async def save_rate(
    bank_name: str,
    bank_url: str,
    buy: float,
    sell: float,
    bank_update: str,
):
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute(
            """
            INSERT INTO bank_rates
            (created_at, bank_name, bank_url, buy, sell, bank_update)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().isoformat(),
                bank_name,
                bank_url,
                buy,
                sell,
                bank_update
            )
        )
        await db.commit()

# ==============================
# TELEGRAM
# ==============================


async def send_telegram(text: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    async with aiohttp.ClientSession() as session:
        await session.post(
            url,
            json={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text,
                "parse_mode": "HTML"
            }
        )

# ==============================
# FETCH OUR RATE
# ==============================


async def fetch_our_rate(id: int):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'https://exprivat.com.ua/api/v1/currencys/?exchanger=1&currency={id}') as response:
            data = await response.json()
            buy = data["objects"][0]["buy"]
            sell = data["objects"][0]["sell"]

            return float(buy), float(sell)

# ==============================
# PLAYWRIGHT PARSER
# ==============================


async def fetch_page_html():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )

        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = await context.new_page()

        # 1️⃣ НЕ ждём load
        await page.goto(
            URL,
            wait_until="domcontentloaded",
            timeout=60000
        )
        print("Current URL:", page.url)
        await page.screenshot(path="debug.png", full_page=True)

        # 2️⃣ Даем JS дорендериться
        await page.wait_for_timeout(5000)

        # 3️⃣ Ждём строки таблицы (не div!)
        await page.wait_for_selector(
            "#organizations_table_cash_bank tr",
            timeout=60000
        )

        # USD
        html_usd = await page.content()
        usd_data = parse_table(html_usd)

        # Переключаемся
        await switch_currency(page, "2")  # EUR
        html = await page.content()
        eur_data = parse_table(html)

        await browser.close()

        return usd_data, eur_data

        # html = await page.content()
        # await browser.close()
        # return html


async def switch_currency(page, currency_id: str):

    dropdown = page.locator(
        ".currencies-dropdown:has(.caption[data-currency_id])"
    ).first

    # 1️⃣ открыть меню
    await dropdown.locator("button.dropdown-toggle").click()

    # 2️⃣ кликнуть по валюте
    await dropdown.locator(
        f"a.change_currency_ajax[data-currency_from='{currency_id}']"
    ).click()

    await page.wait_for_timeout(2000)

    # 4️⃣ ждать обновления таблицы
    await page.wait_for_selector(
        "#organizations_table_cash_bank tr",
        timeout=60000
    )


def parse_table(html: str):
    soup = BeautifulSoup(html, "html.parser")

    container = soup.find("div", id="organizations_table_cash_bank")

    if not container:
        return []

    rows = container.find_all("tr")

    results = []

    for row in rows:
        # название банка
        bank_link = row.find("a", class_="break-word")
        if not bank_link:
            continue

        bank_name = bank_link.get_text(strip=True)
        bank_url = bank_link.get("href")

        # все td с data-sortvalue
        tds = row.find_all("td", attrs={"data-sortvalue": True})
        if len(tds) < 3:
            continue

        try:
            bank_update = tds[0]["data-sortvalue"]
            buy_raw = tds[1]["data-sortvalue"]
            sell_raw = tds[2]["data-sortvalue"]
            # logger.debug(
            #     f'{buy_raw}/{sell_raw}          update {bank_update} {bank_name}')

            buy = float(buy_raw.replace(",", "."))
            sell = float(sell_raw.replace(",", "."))

            results.append((bank_name, bank_url, buy, sell, bank_update))

        except Exception:
            print(f'{bank_name} {buy} {sell}')
            continue

    return results


# ✅ Сохранение после отправки
async def save_sent_message(db, message_text):
    message_hash = hash_message(message_text)

    await db.execute(
        "INSERT INTO sent_messages (message_hash) VALUES (?)",
        (message_hash,)
    )
    await db.commit()

# Проверка перед отправкой


async def message_already_sent(db, message_text):
    message_hash = hash_message(message_text)
    today = datetime.now().date()

    query = """
        SELECT 1 FROM sent_messages
        WHERE message_hash = ?
        AND DATE(created_at) = ?
        LIMIT 1
    """

    async with db.execute(query, (message_hash, today)) as cursor:
        result = await cursor.fetchone()
        return result is not None

# ==============================
# MAIN LOGIC
# ==============================


async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.executescript(CREATE_TABLE_SQL)
        await db.commit()


async def main():
    await init_db()

    usd_rates, eur_rates = await fetch_page_html()

    CURRENCIES = {
        "USD": 1,
        "EUR": 3,
    }

    bank_rates = {
        "USD": usd_rates,
        "EUR": eur_rates,
    }

    if not bank_rates:
        logger.debug("Нет данных")
        return

    async with aiosqlite.connect(DB_NAME) as db:

        for currency, rates in bank_rates.items():
            our_buy, our_sell = await fetch_our_rate(CURRENCIES[currency])

            for bank_name, bank_url, bank_buy, bank_sell, bank_update in rates:

                await save_rate(bank_name, bank_url, bank_buy, bank_sell, bank_update)

                # ==========================
                # Проверка покупки
                # ==========================
                if bank_buy - our_buy >= THRESHOLD:

                    diff_buy = round(bank_buy - our_buy, 2)

                    message = (
                        f"⚠️ <b>{bank_name}</b>\n\n📈 Покупка {currency} выше на {diff_buy}\nБанк: {bank_buy}  Мы: {our_buy}")

                    logger.debug(
                        f'{diff_buy >= THRESHOLD} {diff_buy} {bank_name} bank {bank_buy} Мы: {our_buy}  update {bank_update}')

                    if not await message_already_sent(db, message):
                        await send_telegram(message)
                        await save_sent_message(db, message)
                        logger.info(
                            f"Отправлено сообщение по покупке: {bank_name}")
                    else:
                        logger.debug("Сообщение уже отправлялось сегодня")

                # Проверка продажи
                if our_sell - bank_sell >= THRESHOLD:

                    diff_sell = round(our_sell - bank_sell, 2)

                    logger.debug(
                        f'{our_sell - bank_sell >= THRESHOLD} {diff_sell} {bank_name} bank {bank_sell} мы {our_sell} update {bank_update}')

                    message = (
                        f"⚠️ <b>{bank_name}</b>\n\n📉 Продажа {currency} ниже на {diff_sell}\nБанк: {bank_sell}  Мы: {our_sell}")

                    if not await message_already_sent(db, message):
                        if not await message_already_sent(db, message):
                            await send_telegram(message)
                            await save_sent_message(db, message)
                            logger.info(
                                f"Отправлено сообщение по продаже: {bank_name}")
                        else:
                            logger.debug("Сообщение уже отправлялось сегодня")


if __name__ == "__main__":
    asyncio.run(main())
