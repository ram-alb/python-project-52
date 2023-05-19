from django.apps import AppConfig


class TasksConfig(AppConfig):
    """Configuration class for the tasks app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'task_manager.tasks'
