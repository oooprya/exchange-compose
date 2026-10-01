from loguru import logger
from decimal import Decimal
from services import api_client
from config import API_URL_CURRENCYS, API_BASE

from services.constants import DISCOUNT_USD, DISCOUNT_USD_NEW, DISCOUNT_EUR


@logger.catch
async def get_currencies():
    data = await api_client.get(API_URL_CURRENCYS)
    return data["objects"]


@logger.catch
async def update_currency(curr_id: str, buy: Decimal, sell: Decimal):
    payload = {
        "buy": str(buy),
        "sell": str(sell),
        "updatedAt": ""
    }
    await api_client.patch(
        f"{API_BASE}/api/v1/currencys/{curr_id}/",
        json_data=payload
    )


@logger.catch
def apply_discount(code: str, buy: Decimal, exchanger: str) -> Decimal:
    if exchanger[-2] != "4":
        return buy

    if code == "usd":
        return buy - DISCOUNT_USD
    if code == "usdnew":
        return buy - DISCOUNT_USD_NEW
    if code == "eur":
        return buy - DISCOUNT_EUR

    return buy
