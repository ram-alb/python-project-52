from django.contrib.auth.models import User


class CustomUser(User):
    """Model representing a user."""

    class Meta:
        proxy = True

    def __str__(self):
        """Return a string representation of the user."""
        return f'{self.first_name} {self.last_name}'
