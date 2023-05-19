from django.contrib.auth.models import User
from django.db import models

from task_manager.statuses.models import Statuses

max_length = 150


class Tasks(models.Model):
    """Model representing a status."""

    name = models.CharField(max_length=max_length)
    description = models.TextField()
    status = models.ForeignKey(Statuses, on_delete=models.PROTECT)
    author = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='authored_tasks',
    )
    executor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='executed_tasks',
    )
    created_at = models.DateTimeField(auto_now_add=True)
