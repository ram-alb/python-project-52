from django.db import models

from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.users.models import CustomUser

max_length = 150


class Task(models.Model):
    """Model representing a task."""

    name = models.CharField(max_length=max_length, unique=True)
    description = models.TextField()
    status = models.ForeignKey(Status, on_delete=models.PROTECT)
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
    labels = models.ManyToManyField(Label)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the task."""
        return self.name
