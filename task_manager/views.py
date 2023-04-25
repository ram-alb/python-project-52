from django.shortcuts import render


def index(request):
    """
    Render the index page template.

    Args:
        request (HttpRequest): The HTTP request sent to the server

    Returns:
        HttpResponse: The HTTP response with the rendered HTML of the index page
    """
    return render(request, 'index.html')
