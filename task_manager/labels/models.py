from django.db import models


class Labels(models.Model):
    """Model representing a label."""

    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """Return a string representation of the label."""
        return self.name
