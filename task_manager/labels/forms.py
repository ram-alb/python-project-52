from django import forms
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Labels


class LabelCreattionForm(forms.ModelForm):
    """Form for creating a label."""

    name = forms.CharField(
        label=_('Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Name')}),
    )

    class Meta:
        model = Labels
        fields = ['name']
