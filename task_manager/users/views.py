from django.contrib import messages
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import ListView
from django.views.generic.edit import CreateView

from task_manager.users.forms import UserRegistryForm


class UserListView(ListView):
    """View for displaying a list of all registered users."""

    model = User
    template_name = 'users/user_list.html'


class CreateUserView(CreateView):
    """View for registering a new user."""

    model = User
    form_class = UserRegistryForm
    success_url = reverse_lazy('login')
    template_name = 'users/create_user.html'

    def form_valid(self, form):
        """Handle a valid form submission."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            gettext('User registration was successful'),
        )
        return response
