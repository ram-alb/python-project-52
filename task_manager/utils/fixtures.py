from http import HTTPStatus

from django.contrib.messages import get_messages
from django.urls import reverse


def test_unauthenticated_user(response):
    """
    Test the behavior when an unauthenticated user tries to access a view.

    Args:
        response (HttpResponse): The HTTP response object.

    Raises:
        AssertionError: If the test fails.
    """
    login_url = reverse('login')
    login_message = 'You are not signed in! Please, sign in'

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == login_url
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == login_message


def test_invalid_form(response, model):
    """
    Test the behavior when a form is invalid.

    Args:
        response (HttpResponse): The HTTP response object.

    Raises:
        AssertionError: If the test fails.
    """
    assert response.status_code == HTTPStatus.OK
    assert model.objects.count() == 1
