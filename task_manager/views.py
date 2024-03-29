from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView


class Index(TemplateView):
    """Render the index template."""

    template_name = 'index.html'


class UserLoginView(LoginView):
    """View for logging in a user."""

    template_name = 'login.html'

    def get_success_url(self):
        """Get the URL to redirect to after a successful login."""
        return reverse_lazy('index')

    def form_valid(self, form):
        """Handle a valid form submission."""
        messages.success(self.request, _('You are logged in'))
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    """View for logging out a user."""

    next_page = reverse_lazy('index')

    def dispatch(self, request, *args, **kwargs):
        """Dispatch method for logging the user out."""
        messages.success(self.request, _('You are logged out'))
        return super().dispatch(request, *args, **kwargs)
