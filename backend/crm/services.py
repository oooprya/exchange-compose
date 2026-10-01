# crm/services.py

from decimal import Decimal
from django.db.models import Sum

def update_client_stats(client):

    orders = client.orders.all()

    client.total_orders = orders.count()

    client.total_completed_orders = orders.filter(
        status="completed"
    ).count()

    client.canceled_orders = orders.filter(
        status="cancel"
    ).count()

    client.no_show_count = orders.filter(
        status="noshow"
    ).count()

    client.total_volume = (
        orders.filter(
            status="completed"
        ).aggregate(
            total=Sum("order_sum")
        )["total"] or Decimal("0")
    )

    if client.no_show_count >= 3:
        client.is_blacklisted = True
        client.blacklist_reason = (
            "3 раза не пришел за бронью"
        )

    client.save()