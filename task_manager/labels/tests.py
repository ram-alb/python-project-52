from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from task_manager.labels.models import Labels
from task_manager.statuses.models import Statuses
from task_manager.tasks.models import Tasks
from task_manager.utils.fixtures import test_message, test_unauthenticated_user


class BaseSetup(TestCase):
    """Set up for testing labels app."""

    fixtures = ['users.json', 'statuses.json', 'tasks.json', 'labels.json']

    def setUp(self):
        self.author = User.objects.get(pk=1)
        self.executor = User.objects.get(pk=2)
        self.status = Statuses.objects.get(pk=1)
        self.used_label = Labels.objects.get(pk=1)
        self.task = Tasks.objects.get(pk=1)

        self.labels_list_url = reverse('labels_list')

        self.test_unauthenticated_user = test_unauthenticated_user
        self.test_message = test_message

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
        labels = Labels.objects.all()
        label_names = [label.name for label in labels]

        response = self.client.get(self.labels_list_url)
        response_labels = response.context['object_list']
        response_label_names = [label.name for label in response_labels]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(labels.count(), response_labels.count())
        self.assertListEqual(label_names, response_label_names)

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
        self.assertContains(response, 'Создать метку')

    def test_create_label_view_valid_form(self):
        old_count = Labels.objects.all().count()
        response = self.client.post(self.url, data=self.valid_form)
        label = Labels.objects.last()
        new_count = Labels.objects.all().count()

        self.assertRedirects(response, self.labels_list_url)
        self.test_message(response, 'Метка успешно создана')
        self.assertEqual(label.name, self.valid_form['name'])
        self.assertEqual(new_count, old_count + 1)

    def test_create_label_view_invalid_form(self):
        old_count = Labels.objects.all().count()
        response = self.client.post(self.url, data=self.invalid_form)
        new_count = Labels.objects.all().count()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(old_count, new_count)
        self.assertContains(response, 'Создать метку')


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
        self.assertContains(response, 'Изменение метки')

    def test_update_label_view_valid_form(self):
        old_count = Labels.objects.all().count()
        response = self.client.post(self.url, data=self.valid_form)
        new_count = Labels.objects.all().count()
        label = Labels.objects.get(pk=self.used_label.pk)

        self.assertRedirects(response, self.labels_list_url)
        self.test_message(response, 'Метка успешно изменена')
        self.assertEqual(old_count, new_count)
        self.assertEqual(label.name, self.valid_form['name'])

    def test_update_label_view_invalid_form(self):
        old_count = Labels.objects.all().count()
        response = self.client.post(self.url, data=self.invalid_form)
        new_count = Labels.objects.all().count()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(old_count, new_count)
        self.assertContains(response, 'Изменение метки')


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
        label_name = self.used_label.name

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Удаление метки')
        self.assertContains(
            response,
            f'Вы уверены, что хотите удалить {label_name}?',
            html=False,
        )

    def test_delete_label_valid_form(self):
        old_count = Labels.objects.all().count()
        not_used_label = Labels.objects.get(pk=2)
        url = reverse('delete_label', kwargs={'pk': not_used_label.pk})
        response = self.client.post(url)
        new_count = Labels.objects.all().count()

        self.assertRedirects(response, self.labels_list_url)
        self.test_message(response, 'Метка успешно удалена')

        response = self.client.post(self.url)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.test_message(
            response,
            'Невозможно удалить метку, потому что она используется',
        )
        self.assertEqual(new_count, old_count - 1)
