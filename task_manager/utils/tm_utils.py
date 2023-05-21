from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext


class TaskManagerLoginMixin(LoginRequiredMixin):
    """Mixin for views that require login."""

    login_url = reverse_lazy('login')
    redirect_field_name = None

    def handle_no_permission(self):
        """Handle the case when the user does not signed in."""
        messages.error(
            self.request,
            gettext('You are not signed in! Please, sign in'),
        )
        return super().handle_no_permission()


class TaskManagerFormValidMixin(object):
    """Mixin for views that handle valid forms."""

    def form_valid(self, form):
        """Handle the case when the form is valid."""
        response = super().form_valid(form)
        messages.success(
            self.request,
            self.success_message,
        )
        return response
