from django.views.generic import TemplateView


class Index(TemplateView):
    """Render the index template."""

    template_name = 'index.html'
