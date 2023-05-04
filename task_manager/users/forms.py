from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class UserRegistryForm(UserCreationForm):
    """A form used to create a new user."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        ]
