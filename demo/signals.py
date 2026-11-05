import threading

from django.db import connection
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DemoItem, ReceiverLog

# Used by run_demo.py and tests to make execution order/thread visible.
EXECUTION_EVENTS = []
CALL_SEQUENCE = []


@receiver(post_save, sender=DemoItem)
def demo_item_post_save(sender, instance, created, **kwargs):
    CALL_SEQUENCE.append("receiver")
    EXECUTION_EVENTS.append(
        {
            "event": "receiver",
            "thread_id": threading.get_ident(),
            "in_atomic_block": connection.in_atomic_block,
        }
    )

    # This database write is useful for proving transaction behavior.
    ReceiverLog.objects.create(
        item_name=instance.name,
        receiver_was_in_atomic_block=connection.in_atomic_block,
    )
