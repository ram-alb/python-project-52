from django.db import models
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from task_manager.labels.models import Labels


@receiver(pre_delete, sender=Labels)
def prevent_delete_of_related_labels(sender, instance, **kwargs):
    """Prevents the deletion of related labels."""
    if instance.tasks_set.exists():
        raise models.ProtectedError(
            'The label cannot be deleted because it is in use',
            instance,
        )
