import threading

from django.db import connection, transaction
from django.test import TransactionTestCase

from demo.models import DemoItem, ReceiverLog
from demo.signals import CALL_SEQUENCE, EXECUTION_EVENTS
from rectangle import Rectangle


class SignalBehaviorTests(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        EXECUTION_EVENTS.clear()
        CALL_SEQUENCE.clear()

    def test_receiver_runs_synchronously_and_in_same_thread(self):
        caller_thread = threading.get_ident()
        CALL_SEQUENCE.append("caller: before")
        DemoItem.objects.create(name="sync-test")
        CALL_SEQUENCE.append("caller: after")

        self.assertEqual(len(EXECUTION_EVENTS), 1)
        self.assertEqual(EXECUTION_EVENTS[0]["event"], "receiver")
        self.assertEqual(
            CALL_SEQUENCE,
            ["caller: before", "receiver", "caller: after"],
        )
        self.assertEqual(EXECUTION_EVENTS[0]["thread_id"], caller_thread)

    def test_receiver_runs_in_autocommit_without_outer_atomic(self):
        self.assertFalse(connection.in_atomic_block)

        DemoItem.objects.create(name="autocommit-test")

        self.assertFalse(EXECUTION_EVENTS[-1]["in_atomic_block"])
        self.assertTrue(DemoItem.objects.filter(name="autocommit-test").exists())
        self.assertTrue(ReceiverLog.objects.filter(item_name="autocommit-test").exists())

    def test_receiver_database_write_rolls_back_with_outer_atomic(self):
        with self.assertRaises(RuntimeError):
            with transaction.atomic():
                DemoItem.objects.create(name="rollback-test")
                self.assertTrue(EXECUTION_EVENTS[-1]["in_atomic_block"])
                self.assertTrue(DemoItem.objects.filter(name="rollback-test").exists())
                self.assertTrue(ReceiverLog.objects.filter(item_name="rollback-test").exists())
                raise RuntimeError("force rollback")

        self.assertFalse(DemoItem.objects.filter(name="rollback-test").exists())
        self.assertFalse(ReceiverLog.objects.filter(item_name="rollback-test").exists())


class RectangleTests(TransactionTestCase):
    def test_rectangle_iteration_order_and_format(self):
        rectangle = Rectangle(length=12, width=7)
        self.assertEqual(
            list(rectangle),
            [{"length": 12}, {"width": 7}],
        )

    def test_rectangle_requires_integer_dimensions(self):
        with self.assertRaises(TypeError):
            Rectangle(length="12", width=7)
