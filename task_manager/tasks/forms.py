from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Label
from task_manager.statuses.models import Status
from task_manager.tasks.models import Task
from task_manager.users.models import CustomUser


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
        queryset=Status.objects.all(),
    )
    executor = forms.ModelChoiceField(
        label=_('Executor'),
        queryset=CustomUser.objects.all(),
        required=False,
    )
    labels = forms.ModelMultipleChoiceField(
        label=_('Labels'),
        required=False,
        queryset=Label.objects.all(),
    )

    def clean_name(self):
        """Check if label with the same name already exists."""
        name = self.cleaned_data['name']
        if Task.objects.filter(name=name).exists():
            raise ValidationError(_('Task with this name already exists.'))
        return name

    class Meta:
        model = Task
        fields = ['name', 'description', 'status', 'executor', 'labels']
