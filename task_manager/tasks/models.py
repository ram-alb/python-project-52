from django.db import models

from task_manager.labels.models import Labels
from task_manager.statuses.models import Statuses
from task_manager.users.models import CustomUser

max_length = 150


class Tasks(models.Model):
    """Model representing a task."""

    name = models.CharField(max_length=max_length)
    description = models.TextField()
    status = models.ForeignKey(Statuses, on_delete=models.PROTECT)
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='authored_tasks',
    )
    executor = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='executed_tasks',
    )
    labels = models.ManyToManyField(Labels)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the task."""
        return self.name
