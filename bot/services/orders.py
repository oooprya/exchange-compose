from services.api import api


async def create_order(
    currency: str,
    amount: float,
    name: str,
    phone: str,
    address: str
):

    payload = {
        "currency": currency,
        "amount": amount,
        "client_name": name,
        "client_phone": phone,
        "address": address
    }

    data = await api.post(
        "/orders/",
        json=payload
    )

    return {
        "success": True,
        "order_id": data["id"],
        "address": address,
        "currency": currency,
        "amount": amount
    }


async def cancel_order(order_id: int):

    await api.patch(
        f"/orders/{order_id}/",
        json={
            "status": "cancel"
        }
    )

    return {
        "success": True,
        "order_id": order_id
    }


async def order_status(order_id: int):

    data = await api.get(
        f"/orders/{order_id}/"
    )

    return data