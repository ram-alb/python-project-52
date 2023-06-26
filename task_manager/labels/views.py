from django.contrib import messages
from django.db.models.deletion import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from task_manager.labels.forms import LabelCreattionForm
from task_manager.labels.models import Labels
from task_manager.utils.tm_utils import (
    TaskManagerFormValidMixin,
    TaskManagerLoginMixin,
)


class LabelsMixin(TaskManagerLoginMixin, TaskManagerFormValidMixin):
    """Mixin class provides common functionality for labels-related views."""

    model = Labels
    success_url = reverse_lazy('labels_list')


class LabelsListView(LabelsMixin, ListView):
    """A view for displaying a list of labels."""

    template_name = 'labels/labels_list.html'


class CreateLabelView(LabelsMixin, CreateView):
    """A view for creating a new label."""

    form_class = LabelCreattionForm
    template_name = 'labels/create_label.html'
    success_message = gettext('The label was successfully created')


class DeleteLabelView(LabelsMixin, DeleteView):
    """A view for deleting a label."""

    template_name = 'labels/delete_label.html'
    success_message = gettext("The label was successfully deleted")

    def get_context_data(self, **kwargs):
        """Add a message to a context."""
        context = super().get_context_data(**kwargs)
        label_name = self.object.name
        message = gettext(
            'Are you sure you want to delete the %s?',
        ) % label_name
        context['message'] = gettext(message)
        return context

    def form_valid(self, form):
        """Handle the case when the form is valid."""
        try:
            return super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                gettext('The label cannot be deleted because it is in use'),
            )
            return redirect(self.success_url)


class UpdateLabelView(LabelsMixin, UpdateView):
    """A view for updating a label."""

    success_message = gettext('The label was successfully updated')
    template_name = 'labels/update_label.html'
    form_class = LabelCreattionForm
