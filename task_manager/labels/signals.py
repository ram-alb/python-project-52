from django.db import models


def prevent_delete_of_related_labels(sender, instance, *args, **kwargs):
    """Prevents the deletion of related labels."""
    if instance.tasks_set.exists():
        raise models.ProtectedError(
            'The label cannot be deleted because it is in use',
            instance,
        )
