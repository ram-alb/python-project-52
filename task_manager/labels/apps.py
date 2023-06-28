from django.apps import AppConfig


class LabelsConfig(AppConfig):
    """Configuration class for the labels app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_manager.labels'

    def ready(self):
        from django.db.models.signals import pre_delete

        from task_manager.labels.models import Labels
        from task_manager.labels.signals import (
            prevent_delete_of_related_labels,
        )
        pre_delete.connect(prevent_delete_of_related_labels, sender=Labels)
