from django.db.models.signals import pre_save, post_save
 
from django.dispatch import receiver

from currency.models import Orders
from crm.models import ClientProfile
from crm.services import update_client_stats


@receiver(post_save, sender=Orders)
def update_client(sender, instance, **kwargs):

    client = getattr(instance, 'client', None)
    if client:
        update_client_stats(client)

@receiver(pre_save, sender=Orders)
def attach_client(sender, instance, **kwargs):

    if not instance.clients_telephone:
        return

    phone = instance.clients_telephone.strip()

    client, _ = ClientProfile.objects.get_or_create(
        phone=phone
    )

    instance.client = client


@receiver(pre_save, sender=Orders)
def handle_noshow(sender, instance, **kwargs):

    if not instance.pk:
        return

    old = Orders.objects.get(pk=instance.pk)
    client = getattr(instance, 'client', None)

    if (
        old.status != "noshow"
        and instance.status == "noshow"
        and client
    ):

        client.no_show_count += 1

        if client.no_show_count >= 3:
            client.is_blacklisted = True
            client.blacklist_reason = (
                "3 раза не пришел за бронью"
            )

        client.save()