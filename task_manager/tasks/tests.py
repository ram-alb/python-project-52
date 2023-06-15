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
    """Base test case class with common setup data and methods."""

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
        self.task = Tasks.objects.create(
            name='task',
            status=self.status,
            author=self.author,
            executor=self.executor,
        )

        self.valid_data = {
            'name': 'New Task',
            'description': 'new task description',
            'status': self.status.id,
            'executor': self.executor.id,
        }

        self.invalid_data = {
            'name': 'New Task',
            'description': 'new task description',
            'status': '',
            'executor': '',
        }

        self.tasks_list_url = reverse('tasks_list')

        self.test_unauthenticated_user = test_unauthenticated_user
        self.test_invalid_form = test_invalid_form

        self.client = Client()
        self.client.force_login(self.author)


class TasksListViewTest(BaseSetup):
    """Test case class for the TasksListView."""

    def test_tasks_list_view_with_authenticated_user(self):
        response = self.client.get(self.tasks_list_url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.task.name)

    def test_tasks_list_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.tasks_list_url)
        self.test_unauthenticated_user(response)


class CreateTaskViewTest(BaseSetup):
    """Test case class for the CreateTaskView."""

    def setUp(self):
        super().setUp()
        self.url = reverse('create_task')

    def test_create_task_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_create_task_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Create task')

    def test_create_task_view_valid_form(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.tasks_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The task was successfully created',
        )
        task = Tasks.objects.last()
        self.assertEqual(task.name, self.valid_data['name'])
        self.assertEqual(Tasks.objects.count(), 2)

    def test_create_task_view_invalid_form(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.test_invalid_form(response, Tasks)


class UpdateTaskViewTest(BaseSetup):
    """Test case class for the UpdateTaskView."""

    def setUp(self):
        super().setUp()
        self.url = reverse('update_task', kwargs={'pk': self.task.pk})

    def test_update_task_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_update_task_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Update task')

    def test_update_task_view_valid_form(self):
        response = self.client.post(self.url, data=self.valid_data)
        self.assertRedirects(response, self.tasks_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The task was successfully updated',
        )
        task = Tasks.objects.last()
        self.assertEqual(task.name, self.valid_data['name'])
        self.assertEqual(Tasks.objects.count(), 1)

    def test_update_task_view_invalid_form(self):
        response = self.client.post(self.url, data=self.invalid_data)
        self.test_invalid_form(response, Tasks)


class DeleteTaskViewTest(BaseSetup):
    """Test case class for the DeleteTaskView."""

    def setUp(self):
        super().setUp()
        self.url = reverse('delete_task', kwargs={'pk': self.task.pk})

    def test_delete_task_view_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.test_unauthenticated_user(response)

    def test_delete_task_view_authenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Delete task')
        task_name = self.task.name
        self.assertContains(
            response,
            f'Are you sure you want to delete the {task_name}?',
            html=False,
        )

    def test_delete_task_valid_form(self):
        response = self.client.post(self.url)

        self.assertRedirects(response, self.tasks_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'The task was successfully deleted',
        )


class TasksFilterTestCase(TestCase):
    """Test for tasks filter."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password=passw,
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password=passw,
        )
        self.status = Statuses.objects.create(name='Pending')
        self.status2 = Statuses.objects.create(name='Very Urgent')
        self.label = Labels.objects.create(name='Important')
        self.task1 = Tasks.objects.create(
            name='Task 1',
            description='Description 1',
            status=self.status,
            author=self.user,
            executor=self.user,
        )
        self.task1.labels.add(self.label)
        self.task2 = Tasks.objects.create(
            name='Task 2',
            description='Description 2',
            status=self.status2,
            author=self.user2,
            executor=self.user2,
        )
        self.client = Client()
        self.client.force_login(self.user)
        self.url = reverse('tasks_list')

    def test_tasks_filter_with_status(self):
        response = self.client.get(self.url, {'status': self.status.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.task1.name)
        self.assertNotContains(response, self.task2.name)

    def test_tasks_filter_with_executor(self):
        response = self.client.get(self.url, {'executor': self.user.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.task1.name)
        self.assertNotContains(response, self.task2.name)

    def test_tasks_filter_with_labels(self):
        response = self.client.get(self.url, {'labels': self.label.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.task1.name)
        self.assertNotContains(response, self.task2.name)

    def test_tasks_filter_with_self_tasks(self):
        response = self.client.get(self.url, {'self_tasks': 'true'})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.task1.name)
        self.assertNotContains(response, self.task2.name)
