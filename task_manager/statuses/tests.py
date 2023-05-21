from http import HTTPStatus

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from task_manager.statuses.models import Statuses
from task_manager.utils.fixtures import (
    test_invalid_form,
    test_unauthenticated_user,
)


class BaseSetupTestCase(TestCase):
    """Set up for testing statuses app."""

    def setUp(self):
        self.username = 'testuser'
        self.passw = 'testpass'

        self.user = User.objects.create_user(
            username=self.username,
            password=self.passw,
        )
        self.status = Statuses.objects.create(name='Test Status')

        self.login_url = reverse('login')
        self.statuses_list_url = reverse('statuses_list')

        self.valid_form = {
            'name': 'New Status',
        }

        self.test_unauthenticated_user = test_unauthenticated_user
        self.test_invalid_form = test_invalid_form

        self.client = Client()
        self.client.login(username=self.username, password=self.passw)


class CreateStatusViewTestCase(BaseSetupTestCase):
    """Test status creating view."""

    def setUp(self):
        super().setUp()
        self.url = reverse('create_status')

    def test_create_status_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'statuses/create_status.html')

    def test_create_status_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_create_status_view_valid_form(self):
        response = self.client.post(self.url, data=self.valid_form)
        self.assertRedirects(response, self.statuses_list_url)
        self.assertEqual(Statuses.objects.count(), 2)
        status = Statuses.objects.last()
        self.assertEqual(status.name, 'New Status')

    def test_create_status_view_invalid_form(self):
        invalid_form = {'name': ''}
        response = self.client.post(self.url, data=invalid_form)
        self.test_invalid_form(response, Statuses)


class UpdateStatusViewTestCase(BaseSetupTestCase):
    """Test status updating view."""

    def setUp(self):
        super().setUp()
        self.url = reverse('update_status', kwargs={'pk': self.status.pk})
        self.new_status_data = {
            'name': 'New Status',
        }

    def test_update_status_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_update_status_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'statuses/update_status.html')

    def test_update_status_view_post(self):
        response = self.client.post(self.url, data=self.new_status_data)
        self.assertRedirects(response, self.statuses_list_url)

        updated_status = Statuses.objects.get(pk=self.status.pk)
        self.assertEqual(updated_status.name, 'New Status')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The status was successfully updated',
        )


class DeleteStatusViewTestCase(BaseSetupTestCase):
    """Test status deleting view."""

    def setUp(self):
        super().setUp()
        self.url = reverse('delete_status', kwargs={'pk': self.status.pk})

    def test_delete_status_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_delete_status_view_authenticated_user(self):
        response = self.client.get(self.url)

        self.assertContains(response, 'Status deleting', html=False)
        status_name = self.status.name
        self.assertContains(
            response,
            f'Are you sure you want to delete the {status_name}?',
            html=False,
        )

        response = self.client.post(self.url)

        self.assertRedirects(response, self.statuses_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The status was successfully deleted',
        )

        self.assertFalse(Statuses.objects.filter(pk=self.status.pk).exists())
