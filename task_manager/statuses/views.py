from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.statuses.forms import StatusCreationForm
from task_manager.statuses.models import Statuses


class StatusesListView(LoginRequiredMixin, ListView):
    """View for displaying a list of statuses."""

    model = Statuses
    template_name = 'statuses/statuses_list.html'
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def handle_no_permission(self):
        """Handle the case when the user does not signed in."""
        messages.error(
            self.request,
            gettext('You are not signed in! Please, sign in'),
        )
        return super().handle_no_permission()


class StatusMixin(LoginRequiredMixin):
    """Mixin class for status views."""

    model = Statuses
    success_url = reverse_lazy('statuses_list')
    login_url = reverse_lazy('login')
    redirect_field_name = None

    def handle_no_permission(self):
        """Handle the case when the user does not signed in."""
        messages.error(
            self.request,
            gettext('You are not signed in! Please, sign in'),
        )
        return super().handle_no_permission()

    def form_valid(self, form):
        """Handle the case when the form is valid."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            self.success_message,
        )
        return response


class CreateStatusView(StatusMixin, CreateView):
    """View for creating a new status."""

    success_message = gettext('The status was successfully created')
    template_name = 'statuses/create_status.html'
    form_class = StatusCreationForm


class UpdateStatusView(StatusMixin, UpdateView):
    """View for updating an existing status."""

    success_message = gettext('The status was successfully updated')
    template_name = 'statuses/update_status.html'
    form_class = StatusCreationForm


class DeleteStatusView(StatusMixin, DeleteView):
    """View for deleting a status."""

    template_name = 'statuses/delete_status.html'
    success_message = gettext("The status was successfully deleted")

    def get_context_data(self, **kwargs):
        """Return context for deleting a status view."""
        context = super().get_context_data(**kwargs)
        status_name = self.object.name
        message = 'Are you sure you want to delete the %s?' % status_name
        context['message'] = gettext(message)
        return context
