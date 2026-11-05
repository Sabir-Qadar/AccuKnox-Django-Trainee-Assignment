from django.db import models


class DemoItem(models.Model):
    name = models.CharField(max_length=100)


class ReceiverLog(models.Model):
    item_name = models.CharField(max_length=100)
    receiver_was_in_atomic_block = models.BooleanField()
