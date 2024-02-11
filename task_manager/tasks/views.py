from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DeleteView, DetailView, UpdateView
from django_filters.views import FilterView

from task_manager.tasks.filters import TasksFilter
from task_manager.tasks.forms import TaskCreationForm
from task_manager.tasks.models import Task
from task_manager.utils.tm_utils import (
    TaskManagerFormValidMixin,
    TaskManagerLoginMixin,
)


class TasksMixin(TaskManagerLoginMixin, TaskManagerFormValidMixin):
    """Mixin class that provides common functionality for task-related views."""

    model = Task
    success_url = reverse_lazy('tasks_list')


class TasksListView(TasksMixin, FilterView):
    """A view for displaying a list of tasks."""

    template_name = 'tasks/tasks_list.html'
    filterset_class = TasksFilter


class CreateTaskView(TasksMixin, CreateView):
    """A view for creating a new task."""

    form_class = TaskCreationForm
    template_name = 'tasks/create_task.html'
    success_message = _('The task was successfully created')

    def form_valid(self, form):
        """Handle the case when the form is valid."""
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateTaskView(TasksMixin, UpdateView):
    """A view for updating an existing task."""

    success_url = reverse_lazy('tasks_list')
    form_class = TaskCreationForm
    template_name = 'tasks/update_task.html'
    success_message = _('The task was successfully updated')


class DeleteTaskView(TasksMixin, DeleteView):
    """A view for deleting a task."""

    success_url = reverse_lazy('tasks_list')
    success_message = _("The task was successfully deleted")
    template_name = 'tasks/delete_task.html'

    def get_context_data(self, **kwargs):
        """Return context for the delete task view."""
        context = super().get_context_data(**kwargs)
        message = _(
            'Are you sure you want to delete the %s?',
        ) % self.object
        context['message'] = message
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        self.object = self.get_object()

        if self.object.author != self.request.user:
            messages.error(
                self.request,
                _('Only the author can delete the task'),
            )
            return redirect('tasks_list')

        return super().get(request, *args, **kwargs)


class TaskDetailView(TasksMixin, DetailView):
    """A view for displaying detailed information about a task."""

    template_name = 'tasks/task_detail.html'
