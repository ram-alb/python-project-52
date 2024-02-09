import django_filters
from django import forms

from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.models import CustomUser


class TasksFilter(django_filters.FilterSet):
    """Filter for tasks."""

    status = django_filters.ModelChoiceFilter(
        label='',
        queryset=Status.objects.all(),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    executor = django_filters.ModelChoiceFilter(
        label='',
        queryset=CustomUser.objects.all(),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    labels = django_filters.ModelChoiceFilter(
        label='',
        queryset=Label.objects.all(),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Task
        fields = ['status', 'executor', 'labels']

    @property
    def qs(self):
        """Return the queryset that will be used to display Task objects."""
        parent = super().qs
        self_tasks = self.request.GET.get('self_tasks')
        user = self.request.user
        if self_tasks:
            return parent.filter(author=user)
        return parent

    def is_valid(self):
        """Check if the form associated with the filter is valid."""
        if self.form.is_valid():
            for field_name, field in self.form.fields.items():
                if field_name in self.form.cleaned_data:
                    field.widget.attrs['class'] = 'form-control is-valid'
        return super().is_valid
