from http import HTTPStatus

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

from task_manager.labels.models import Labels
from task_manager.statuses.models import Statuses
from task_manager.tasks.models import Tasks
from task_manager.utils.fixtures import (
    test_invalid_form,
    test_unauthenticated_user,
)

passw = 'pass'


class BaseSetup(TestCase):
    """Set up for testing labels app."""

    def setUp(self):
        """Set up the test data."""
        self.author = User.objects.create(
            username='author',
            password=passw,
        )
        self.executor = User.objects.create(
            username='executor',
            password=passw,
        )
        self.status = Statuses.objects.create(name='Done')
        self.used_label = Labels.objects.create(name='used_label')
        self.task = Tasks.objects.create(
            name='task',
            status=self.status,
            author=self.author,
            executor=self.executor,
        )
        self.task.labels.add(self.used_label)

        self.labels_list_url = reverse('labels_list')

        self.test_unauthenticated_user = test_unauthenticated_user
        self.test_invalid_form = test_invalid_form

        self.valid_form = {
            'name': 'New Label',
        }
        self.invalid_form = {
            'name': '',
        }

        self.client = Client()
        self.client.force_login(self.author)


class LabelsListViewTest(BaseSetup):
    """Test case class for the LabelsListView."""

    def test_labels_list_view_with_authenticated_user(self):
        response = self.client.get(self.labels_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.used_label.name)

    def test_labels_list_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.labels_list_url)
        self.test_unauthenticated_user(response)


class CreateLabelViewTest(BaseSetup):
    """Test case class for the CreateLabelView."""

    def setUp(self):
        super().setUp()
        self.url = reverse('create_label')

    def test_create_label_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_create_label_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Create label')

    def test_create_label_view_valid_form(self):
        response = self.client.post(self.url, data=self.valid_form)
        self.assertRedirects(response, self.labels_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The label was successfully created',
        )
        label = Labels.objects.last()
        self.assertEqual(label.name, self.valid_form['name'])
        self.assertEqual(Labels.objects.count(), 2)

    def test_create_label_view_invalid_form(self):
        response = self.client.post(self.url, data=self.invalid_form)
        self.test_invalid_form(response, Labels)


class UpdateLabelViewTest(BaseSetup):
    """Test case class for the UpdateLabelView."""

    def setUp(self):
        super().setUp()
        self.url = reverse('update_label', kwargs={'pk': self.used_label.pk})

    def test_update_label_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_update_label_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Update label')

    def test_update_label_view_valid_form(self):
        response = self.client.post(self.url, data=self.valid_form)
        self.assertRedirects(response, self.labels_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The label was successfully updated',
        )
        label = Labels.objects.last()
        self.assertEqual(label.name, self.valid_form['name'])
        self.assertEqual(Tasks.objects.count(), 1)

    def test_update_label_view_invalid_form(self):
        response = self.client.post(self.url, data=self.invalid_form)
        self.test_invalid_form(response, Labels)


class DeleteLabelViewTest(BaseSetup):
    """Test case class for the DeleteLabelView."""

    def setUp(self):
        super().setUp()
        self.url = reverse('delete_label', kwargs={'pk': self.used_label.pk})

    def test_delete_label_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_delete_label_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Label deleting')
        label_name = self.used_label.name
        self.assertContains(
            response,
            f'Are you sure you want to delete the {label_name}?',
            html=False,
        )

    def test_delete_label_valid_form(self):
        not_used_label = Labels.objects.create(name='not used label')
        url = reverse('delete_label', kwargs={'pk': not_used_label.pk})
        response = self.client.post(url)

        self.assertRedirects(response, self.labels_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The label was successfully deleted',
        )

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The label cannot be deleted because it is in use',
        )
