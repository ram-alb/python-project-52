from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Labels
from task_manager.statuses.models import Statuses
from task_manager.tasks.models import Tasks


class TaskCreationForm(forms.ModelForm):
    """Form for creating a task."""

    name = forms.CharField(
        label=_('Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Name')}),
    )
    description = forms.CharField(
        label=_('Description'),
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': _('Description'),
            'rows': 10,
            'cols': 40,
        }),
    )
    status = forms.ModelChoiceField(
        label=_('Status'),
        queryset=Statuses.objects.all(),
    )
    executor = forms.ModelChoiceField(
        label=_('Executor'),
        queryset=User.objects.all(),
    )
    labels = forms.ModelMultipleChoiceField(
        label=_('Labels'),
        required=False,
        queryset=Labels.objects.all(),
    )

    class Meta:
        model = Tasks
        fields = ['name', 'description', 'status', 'executor', 'labels']
