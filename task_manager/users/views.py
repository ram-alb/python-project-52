from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import DeleteView, ListView, UpdateView
from django.views.generic.edit import CreateView

from task_manager.users.forms import UserRegistryForm
from task_manager.utils.tm_utils import (
    TaskManagerFormValidMixin,
    TaskManagerLoginMixin,
)


class UsersMixin(TaskManagerLoginMixin, TaskManagerFormValidMixin):
    """Mixin class that provides common functionality for users app views."""

    model = User
    success_url = reverse_lazy('user_list')


class UserListView(ListView):
    """View for displaying a list of all registered users."""

    model = User
    template_name = 'users/user_list.html'


class CreateUserView(TaskManagerFormValidMixin, CreateView):
    """View for registering a new user."""

    model = User
    form_class = UserRegistryForm
    success_url = reverse_lazy('login')
    template_name = 'users/create_user.html'
    success_message = gettext('User registration was successful')


class UserUpdateView(UsersMixin, UpdateView):
    """A view to update a user's information."""

    form_class = UserRegistryForm
    template_name = 'users/update_user.html'
    success_message = gettext('The user has been successfully updated')

    def dispatch(self, request, *args, **kwargs):
        """Edit the profile if the user is authenticated and authorized."""
        if not request.user.is_authenticated:
            messages.error(
                request,
                gettext('You are not signed in! Please, sign in'),
            )
            return redirect('login')
        elif self.get_object().pk != request.user.pk:
            messages.error(
                request,
                gettext("You don't have the rights to modify another user."),
            )
            return redirect('user_list')

        return super().dispatch(request, *args, **kwargs)


class UserDeleteView(UsersMixin, DeleteView):
    """A view to delete a user's profile."""

    template_name = 'users/delete_user.html'
    success_message = gettext("The user was successfuly deleted")

    def get_context_data(self, **kwargs):
        """Return the context data for the view."""
        context = super().get_context_data(**kwargs)
        full_name = '{first_name} {last_name}'.format(
            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
        )
        message = gettext('Are you sure you want to delete the %s?') % full_name
        context['message'] = message
        return context

    def dispatch(self, request, *args, **kwargs):
        """Delete the profile if the user is authenticated and authorized."""
        if not request.user.is_authenticated:
            messages.error(
                request,
                gettext('You are not signed in! Please, sign in.'),
            )
            return redirect('login')
        elif self.get_object().pk != request.user.pk:
            messages.error(
                request,
                gettext("You don't have the rights to modify another user."),
            )
            return redirect('user_list')

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Call when a valid form has been submitted."""
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                'Unable to delete the user because it is in use',
            )

            return redirect(self.success_url)
