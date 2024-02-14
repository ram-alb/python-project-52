from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task_manager.statuses.models import Status


class StatusCreationForm(forms.ModelForm):
    """Form for creating a status."""

    name = forms.CharField(
        label=_('Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Name')}),
    )

    def clean_name(self):
        """Check if label with the same name already exists."""
        name = self.cleaned_data['name']
        if Status.objects.filter(name=name).exists():
            raise ValidationError(_('Status with this name already exists.'))
        return name

    class Meta:
        model = Status
        fields = ['name']
