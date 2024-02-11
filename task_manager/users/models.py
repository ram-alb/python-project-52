from django.contrib.auth.models import User


class CustomUser(User):
    """Model representing a user."""

    class Meta:
        proxy = True

    def __str__(self):
        """Return a string representation of the user."""
        return self.get_full_name()
