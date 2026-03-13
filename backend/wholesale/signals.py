from django.db.models.signals import post_save
from django.dispatch import receiver
from wholesale.models import CashBalance
from wholesale.services.balance_service import broadcast_node


@receiver(post_save, sender=CashBalance)
def update_node_dashboard(sender, instance, **kwargs):
    broadcast_node(instance.node_id)
