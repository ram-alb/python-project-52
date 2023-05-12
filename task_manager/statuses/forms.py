from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.statuses.models import Statuses


class StatusCreationForm(forms.ModelForm):
    """Form for creating a status."""

    name = forms.CharField(
        label=_('Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Name')}),
    )

    class Meta:
        model = Statuses
        fields = ['name']
