from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from task_manager.statuses.models import Status
from task_manager.utils.fixtures import test_message, test_unauthenticated_user


class BaseSetupTestCase(TestCase):
    """Set up for testing statuses app."""

    fixtures = ['users.json', 'statuses.json', 'tasks.json', 'labels.json']

    def setUp(self):
        self.login_url = reverse('login')
        self.statuses_list_url = reverse('statuses_list')
        self.status = Status.objects.get(pk=1)
        self.valid_form = {'name': 'New Status'}
        self.test_unauthenticated_user = test_unauthenticated_user
        self.test_message = test_message
        self.user = User.objects.get(pk=1)
        self.client = Client()
        self.client.force_login(self.user)


class StatusesListViewTestCase(BaseSetupTestCase):
    """Test StatusesListView."""

    def test_statuses_list_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.statuses_list_url)

        self.test_unauthenticated_user(response)

    def test_statuses_list_view_authenticated_user(self):
        statuses = Status.objects.all()
        status_names = [status.name for status in statuses]

        response = self.client.get(self.statuses_list_url)
        response_statuses = [
            status.name for status in response.context['object_list']
        ]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Статусы')
        self.assertEqual(
            response.context['object_list'].count(),
            statuses.count(),
        )
        self.assertListEqual(status_names, response_statuses)


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
        statuses_count_old = Status.objects.all().count()
        response = self.client.post(self.url, data=self.valid_form)
        statuses_count_new = Status.objects.all().count()
        status = Status.objects.last()

        self.assertRedirects(response, self.statuses_list_url)
        self.assertEqual(status.name, 'New Status')
        self.test_message(response, 'Статус успешно создан')
        self.assertEqual(statuses_count_new, statuses_count_old + 1)

    def test_create_status_view_invalid_form(self):
        statuses_count_old = Status.objects.all().count()
        invalid_form = {'name': ''}
        response = self.client.post(self.url, data=invalid_form)
        statuses_count_new = Status.objects.all().count()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Создать статус')
        self.assertEqual(statuses_count_new, statuses_count_old)


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
        updated_status = Status.objects.get(pk=self.status.pk)

        self.assertRedirects(response, self.statuses_list_url)
        self.assertEqual(updated_status.name, 'New Status')
        self.test_message(response, 'Статус успешно изменен')


class DeleteStatusViewTestCase(BaseSetupTestCase):
    """Test status deleting view."""

    def setUp(self):
        super().setUp()
        self.unused_status = Status.objects.last()
        self.url = reverse(
            'delete_status',
            kwargs={'pk': self.unused_status.pk},
        )

    def test_delete_status_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_delete_status_view_authenticated_user(self):
        status_name = self.unused_status.name
        response = self.client.get(self.url)

        self.assertContains(response, 'Удаление статуса')
        self.assertContains(
            response,
            f'Вы уверены, что хотите удалить {status_name}?',
        )

    def test_delete_status_unused(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, self.statuses_list_url)
        self.test_message(response, 'Статус успешно удален')
        self.assertFalse(
            Status.objects.filter(pk=self.unused_status.pk).exists(),
        )

    def test_delete_status_busy(self):
        url = reverse('delete_status', kwargs={'pk': self.status.pk})
        response = self.client.post(url)

        self.assertRedirects(response, self.statuses_list_url)
        self.test_message(
            response,
            'Невозможно удалить статус, потому что он используется',
        )
        self.assertTrue(Status.objects.filter(pk=self.status.pk).exists())
