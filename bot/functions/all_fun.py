import requests
from loguru import logger
from os import getenv
headers = {"Authorization": f"ApiKey {getenv('API_KEY')}"}


@logger.catch
async def status_orders(data_id, data_status):
    order_patch = {"status": f"{data_status}"}
    x = requests.patch(f'{getenv("API")}/api/v1/orders/{data_id}/',
                       json=order_patch, headers=headers)
    logger.debug(x.status_code)
    return order_patch
