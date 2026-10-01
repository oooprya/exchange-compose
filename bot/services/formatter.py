from .constants import CURRENCY_TEMPLATES


def format_currency_row(currency: str, buy: str, sell: str) -> str:
    """
    Возвращает готовую строку валюты и её индекс для вставки.
    """
    tpl, index = CURRENCY_TEMPLATES.get(currency, (None, None))
    if not tpl:
        return None, None

    return tpl.format(buy=buy, sell=sell), index
