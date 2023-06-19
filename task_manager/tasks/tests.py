from http import HTTPStatus

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from task_manager.labels.models import Labels
from task_manager.statuses.models import Statuses
from task_manager.tasks.models import Tasks
from task_manager.utils.fixtures import test_message, test_unauthenticated_user


class BaseSetup(TestCase):
    """Set up tests for tasks app."""

    fixtures = ['users.json', 'statuses.json', 'tasks.json', 'labels.json']

    def setUp(self):
        self.tasks_list_url = reverse('tasks_list')
        self.task = Tasks.objects.get(pk=1)
        self.author = User.objects.get(pk=1)
        self.executor = User.objects.get(pk=2)
        self.status = Statuses.objects.get(pk=1)
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
        self.test_unauthenticated_user = test_unauthenticated_user
        self.test_message = test_message

        self.client.force_login(self.author)


class TasksListViewTest(BaseSetup):
    """Test case class for the TasksListView."""

    def test_tasks_list_view_with_authenticated_user(self):
        tasks = Tasks.objects.all()
        task_names = [task.name for task in tasks]

        response = self.client.get(self.tasks_list_url)
        response_tasks = [task.name for task in response.context['object_list']]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.context['object_list'].count(), tasks.count())
        self.assertListEqual(response_tasks, task_names)

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
        tasks_old = Tasks.objects.all().count()
        response = self.client.post(self.url, data=self.valid_data)
        tasks_new = Tasks.objects.all().count()
        task = Tasks.objects.last()

        self.assertRedirects(response, self.tasks_list_url)
        self.test_message(response, 'The task was successfully created')
        self.assertEqual(task.name, self.valid_data['name'])
        self.assertEqual(tasks_new, tasks_old + 1)

    def test_create_task_view_invalid_form(self):
        tasks_count_old = Tasks.objects.all().count()
        response = self.client.post(self.url, data=self.invalid_data)
        tasks_count_new = Tasks.objects.all().count()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Create task')
        self.assertEqual(tasks_count_new, tasks_count_old)


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
        old_count = Tasks.objects.all().count()
        response = self.client.post(self.url, data=self.valid_data)
        task_name = Tasks.objects.get(pk=self.task.pk).name
        new_count = Tasks.objects.all().count()

        self.assertRedirects(response, self.tasks_list_url)
        self.test_message(response, 'The task was successfully updated')
        self.assertEqual(task_name, self.valid_data['name'])
        self.assertEqual(old_count, new_count)

    def test_update_task_view_invalid_form(self):
        old_count = Tasks.objects.all().count()
        response = self.client.post(self.url, data=self.invalid_data)
        new_count = Tasks.objects.all().count()

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Update task')
        self.assertEqual(old_count, new_count)


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
        task_name = self.task.name

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Delete task')
        self.assertContains(
            response,
            f'Are you sure you want to delete the {task_name}?',
        )

    def test_delete_task_valid_form(self):
        old_count = Tasks.objects.all().count()
        response = self.client.post(self.url)
        new_count = Tasks.objects.all().count()

        self.assertRedirects(response, self.tasks_list_url)
        self.test_message(response, 'The task was successfully deleted')
        self.assertEqual(old_count, new_count + 1)


class TasksFilterTestCase(TestCase):
    """Test for tasks filter."""

    fixtures = ['users.json', 'statuses.json', 'tasks.json', 'labels.json']

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.status1 = Statuses.objects.get(pk=1)
        self.status2 = Statuses.objects.get(pk=2)
        self.label = Labels.objects.get(pk=1)
        self.task1 = Tasks.objects.get(pk=1)
        self.task2 = Tasks.objects.get(pk=2)
        self.url = reverse('tasks_list')
        self.client = Client()
        self.client.force_login(self.user1)

    def test_tasks_filter_with_status(self):
        response = self.client.get(self.url, {'status': self.status1.id})
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, self.task1.name)
        self.assertNotContains(response, self.task2.name)

    def test_tasks_filter_with_executor(self):
        response = self.client.get(self.url, {'executor': self.user2.id})
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
        self.assertContains(response, self.task2.name)
