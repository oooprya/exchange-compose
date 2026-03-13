from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from .balance_service import BalanceService


class DashboardNotifier:

    @staticmethod
    def notify_node(node_id):

        channel_layer = get_channel_layer()

        payload = BalanceService.get_node_balances(node_id)

        async_to_sync(channel_layer.group_send)(
            f"node_{node_id}",
            {
                "type": "balance_update",
                "data": payload
            }
        )

        # если нужно senior видеть всё
        async_to_sync(channel_layer.group_send)(
            "dashboard_global",
            {
                "type": "balance_update",
                "data": payload
            }
        )
