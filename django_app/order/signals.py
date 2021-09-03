from django.db.models.signals import pre_save
from django.dispatch import receiver

from .models import Receiver


@receiver(pre_save, sender=Receiver)
def set_uuid(sender, instance, *args, **kwargs):
    if instance.uuid:
        return
    instance.set_uuid()
