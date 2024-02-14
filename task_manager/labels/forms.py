from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from task_manager.labels.models import Label


class LabelCreattionForm(forms.ModelForm):
    """Form for creating a label."""

    name = forms.CharField(
        label=_('Name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Name')}),
    )

    def clean_name(self):
        """Check if label with the same name already exists."""
        name = self.cleaned_data['name']
        if Label.objects.filter(name=name).exists():
            raise ValidationError(_('Label with this name already exists.'))
        return name

    class Meta:
        model = Label
        fields = ['name']
