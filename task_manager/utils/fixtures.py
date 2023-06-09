from http import HTTPStatus

from django.contrib.messages import get_messages
from django.urls import reverse


def test_message(response, message):
    """
    Test the flash messages in response.

    Args:
        response (HttpResponse): The HTTP response object
        message (str): An expected flash message text

    Raises:
        AssertionError: If the test fails.
    """
    messages = list(get_messages(response.wsgi_request))
    assert len(messages) == 1
    assert str(messages[0]) == message


def test_unauthenticated_user(response):
    """
    Test the behavior when an unauthenticated user tries to access a view.

    Args:
        response (HttpResponse): The HTTP response object.

    Raises:
        AssertionError: If the test fails.
    """
    login_url = reverse('login')
    login_message = 'Вы не авторизованы! Пожалуйста, выполните вход'

    assert response.status_code == HTTPStatus.FOUND
    assert response.url == login_url
    test_message(response, login_message)
