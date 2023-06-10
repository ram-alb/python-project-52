from django.apps import AppConfig


class LabelsConfig(AppConfig):
    """Configuration class for the labels app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_manager.labels'

    def ready(self):
        import task_manager.labels.signals
