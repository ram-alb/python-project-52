import django_filters
from django import forms
from django.contrib.auth.models import User

from task_manager.labels.models import Labels
from task_manager.statuses.models import Statuses
from task_manager.tasks.models import Tasks


class TasksFilter(django_filters.FilterSet):
    """Filter for tasks."""

    status = django_filters.ModelChoiceFilter(
        label='',
        queryset=Statuses.objects.all(),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    executor = django_filters.ModelChoiceFilter(
        label='',
        queryset=User.objects.all(),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    labels = django_filters.ModelChoiceFilter(
        label='',
        queryset=Labels.objects.all(),
        to_field_name='id',
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Tasks
        fields = ['status', 'executor', 'labels']

    @property
    def qs(self):
        parent = super().qs
        self_tasks = self.request.GET.get('self_tasks')
        user = self.request.user
        if self_tasks:
            return parent.filter(author=user)
        return parent

    def is_valid(self):
        if self.form.is_valid():
            for field_name, field in self.form.fields.items():
                if field_name in self.form.cleaned_data:
                    field.widget.attrs['class'] = 'form-control is-valid'
        return super().is_valid
