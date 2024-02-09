from django.db import models


class Label(models.Model):
    """Model representing a label."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the label."""
        return self.name
