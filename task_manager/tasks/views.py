from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.translation import gettext
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from task_manager.tasks.forms import TaskCreationForm
from task_manager.tasks.models import Tasks


class TaskMixin(LoginRequiredMixin):
    """Mixin class that provides common functionality for task-related views."""

    model = Tasks
    success_url = reverse_lazy('tasks_list')

    login_url = reverse_lazy('login')
    redirect_field_name = None

    def handle_no_permission(self):
        """Handle the case when the user is not logged in."""
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


class TasksListView(TaskMixin, ListView):
    """A view for displaying a list of tasks."""

    template_name = 'tasks/tasks_list.html'


class CreateTaskView(TaskMixin, CreateView):
    """A view for creating a new task."""

    form_class = TaskCreationForm
    template_name = 'tasks/create_task.html'
    success_message = gettext('The task was successfully created')

    def form_valid(self, form):
        """Handle the case when the form is valid."""
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdateTaskView(TaskMixin, UpdateView):
    """A view for updating an existing task."""

    success_url = reverse_lazy('tasks_list')
    form_class = TaskCreationForm
    template_name = 'tasks/update_task.html'
    success_message = gettext('The task was successfully updated')


class DeleteTaskView(TaskMixin, DeleteView):
    """A view for deleting a task."""

    success_url = reverse_lazy('tasks_list')
    success_message = gettext("The task was successfully deleted")
    template_name = 'tasks/delete_task.html'

    def get_context_data(self, **kwargs):
        """Return context for the delete task view."""
        context = super().get_context_data(**kwargs)
        task_name = self.object.name
        message = 'Are you sure you want to delete the %s?' % task_name
        context['message'] = gettext(message)
        return context

    def get(self, request, *args, **kwargs):
        """Handle GET requests."""
        self.object = self.get_object()

        if self.object.author != self.request.user:
            messages.error(
                self.request,
                gettext('Only the author can delete the task'),
            )
            return redirect('tasks_list')

        return super().get(request, *args, **kwargs)


class TaskDetailView(TaskMixin, DetailView):
    """A view for displaying detailed information about a task."""

    template_name = 'tasks/task_detail.html'
