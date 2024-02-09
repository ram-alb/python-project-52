from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.statuses.forms import StatusCreationForm
from task_manager.statuses.models import Status
from task_manager.utils.tm_utils import (
    TaskManagerFormValidMixin,
    TaskManagerLoginMixin,
)


class StatusesMixin(TaskManagerLoginMixin, TaskManagerFormValidMixin):
    """Mixin class for status views."""

    model = Status
    success_url = reverse_lazy('statuses_list')


class StatusesListView(StatusesMixin, ListView):
    """View for displaying a list of statuses."""

    template_name = 'statuses/statuses_list.html'


class CreateStatusView(StatusesMixin, CreateView):
    """View for creating a new status."""

    success_message = gettext('The status was successfully created')
    template_name = 'statuses/create_status.html'
    form_class = StatusCreationForm


class UpdateStatusView(StatusesMixin, UpdateView):
    """View for updating an existing status."""

    success_message = gettext('The status was successfully updated')
    template_name = 'statuses/update_status.html'
    form_class = StatusCreationForm


class DeleteStatusView(StatusesMixin, DeleteView):
    """View for deleting a status."""

    template_name = 'statuses/delete_status.html'
    success_message = gettext("The status was successfully deleted")

    def get_context_data(self, **kwargs):
        """Return context for deleting a status view."""
        context = super().get_context_data(**kwargs)
        status_name = self.object.name
        message = gettext(
            'Are you sure you want to delete the %s?',
        ) % status_name
        context['message'] = message
        return context

    def post(self, request, *args, **kwargs):
        try:
            return super().post(request, *args, **kwargs)
        except ProtectedError:
            messages.error(
                self.request,
                gettext(
                    'It is not possible to delete the status '
                    'because it is being used',
                ),
            )
        return redirect(reverse_lazy('statuses_list'))
