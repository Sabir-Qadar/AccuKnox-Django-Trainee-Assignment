import threading

from django.core.management.base import BaseCommand
from django.db import connection, transaction

from demo.models import DemoItem, ReceiverLog
from demo.signals import CALL_SEQUENCE, EXECUTION_EVENTS
from rectangle import Rectangle


class Command(BaseCommand):
    help = "Demonstrate Django signals and the iterable Rectangle class."

    def handle(self, *args, **options):
        DemoItem.objects.all().delete()
        ReceiverLog.objects.all().delete()
        EXECUTION_EVENTS.clear()
        CALL_SEQUENCE.clear()

        self.stdout.write(self.style.MIGRATE_HEADING("Q1: Synchronous execution"))
        CALL_SEQUENCE.append("caller: before save")
        item = DemoItem(name="autocommit-example")
        item.save()
        CALL_SEQUENCE.append("caller: after save")
        self.stdout.write("Observed call order:")
        for event in CALL_SEQUENCE:
            self.stdout.write(f"  {event}")
        self.stdout.write("Conclusion: receiver completed before save() returned.")

        self.stdout.write(self.style.MIGRATE_HEADING("Q2: Same thread"))
        caller_thread_id = threading.get_ident()
        receiver_thread_id = EXECUTION_EVENTS[-1]["thread_id"]
        self.stdout.write(f"Caller thread ID:   {caller_thread_id}")
        self.stdout.write(f"Receiver thread ID: {receiver_thread_id}")
        self.stdout.write(f"Same thread: {caller_thread_id == receiver_thread_id}")

        self.stdout.write(self.style.MIGRATE_HEADING("Q3: Database transaction"))
        self.stdout.write(
            "Default autocommit: receiver in atomic block = "
            f"{EXECUTION_EVENTS[-1]['in_atomic_block']}"
        )
        self.stdout.write(
            "Rows after normal save: "
            f"DemoItem={DemoItem.objects.filter(name='autocommit-example').count()}, "
            f"ReceiverLog={ReceiverLog.objects.filter(item_name='autocommit-example').count()}"
        )

        try:
            with transaction.atomic():
                atomic_item = DemoItem.objects.create(name="atomic-example")
                atomic_event = EXECUTION_EVENTS[-1]
                self.stdout.write(
                    "Inside transaction.atomic(): receiver in atomic block = "
                    f"{atomic_event['in_atomic_block']}"
                )
                raise RuntimeError("Deliberately roll back this transaction")
        except RuntimeError:
            self.stdout.write("Deliberately raised an exception; atomic block rolled back.")

        self.stdout.write(
            "Rows after rollback: "
            f"DemoItem={DemoItem.objects.filter(name='atomic-example').count()}, "
            f"ReceiverLog={ReceiverLog.objects.filter(item_name='atomic-example').count()}"
        )
        self.stdout.write(
            "Conclusion: the receiver's database write rolled back with the caller's "
            "atomic transaction."
        )

        self.stdout.write(self.style.MIGRATE_HEADING("Custom iterable Rectangle"))
        rectangle = Rectangle(length=10, width=5)
        for dimension in rectangle:
            self.stdout.write(str(dimension))
