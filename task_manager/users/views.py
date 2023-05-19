from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import DeleteView, ListView, UpdateView
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


class UserUpdateView(LoginRequiredMixin, UpdateView):
    """A view to update a user's information."""

    model = User
    form_class = UserRegistryForm
    template_name = 'users/update_user.html'
    success_url = reverse_lazy('user_list')

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

    def form_valid(self, form):
        """Call when a valid form has been submitted."""
        messages.success(
            self.request,
            gettext('The user has been successfully updated'),
        )
        return super().form_valid(form)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    """A view to delete a user's profile."""

    model = User
    success_url = reverse_lazy('user_list')
    template_name = 'users/delete_user.html'

    def get_context_data(self, **kwargs):
        """Return the context data for the view."""
        context = super().get_context_data(**kwargs)
        full_name = '{first_name} {last_name}'.format(
            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
        )
        message = 'Are you sure you want to delete the %s?' % full_name
        context['message'] = gettext(message)
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
        messages.success(
            self.request,
            gettext("The user was successfuly deleted"),
        )
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                'Unable to delete the user because it is in use',
            )

            return redirect(self.success_url)
