from django import forms
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _


class UserRegistryForm(forms.ModelForm):
    """A form used to create a new user."""

    first_name = forms.CharField(
        label=_('First name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('First name')}),
    )
    last_name = forms.CharField(
        label=_('Last name'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Last name')}),
    )
    username = forms.CharField(
        label=_('Username'),
        required=True,
        widget=forms.TextInput(attrs={'placeholder': _('Username')}),
        help_text=_(
            'Required field. No more than 150 characters. '
            'Only letters, numbers, and symbols @/./+/-/_',
        ),
    )
    password1 = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')}),
        help_text=_('Your password must contain at least 3 characters.'),
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(
            attrs={'placeholder': _('Password confirmation')},
        ),
        help_text=_('To confirm, please enter your password again.'),
    )

    def clean_password2(self):
        """Check if the password entered by the user."""
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if len(password1) < 3:
            raise forms.ValidationError(
                (
                    'The password entered is too short. '
                    'It must contain at least 3 characters.'
                ),
            )
        if password1 != password2:
            raise forms.ValidationError('The entered passwords do not match.')
        return password2

    def save(self, commit=True):
        """Save a new user."""
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'password1',
            'password2',
        ]
