from http import HTTPStatus

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

valid_form = {
    'first_name': 'John',
    'last_name': 'Doe',
    'username': 'johndoe',
    'password1': 'password',
    'password2': 'password',
}


class UserListViewTestCase(TestCase):
    """Tests for UserListView."""

    fixtures = ['users.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.url = reverse('user_list')

    def assert_user_list_equal(self, response):
        users = User.objects.all()
        user_names = [user.username for user in users]
        response_user_names = [
            user.username for user in response.context['object_list']
        ]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'Users')
        self.assertEqual(response.context['object_list'].count(), users.count())
        self.assertListEqual(user_names, response_user_names)

    def test_users_list_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assert_user_list_equal(response)

    def test_users_list_view_with_authenticated_user(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

        response = self.client.get(self.url)
        self.assert_user_list_equal(response)


class CreateUserViewTestCase(TestCase):
    """Tests for the CreateUserView view."""

    def setUp(self):
        self.url = reverse('create_user')
        self.user_data = valid_form.copy()

    def test_create_user_view_exists(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_user_view_valid_data(self):
        response = self.client.post(self.url, self.user_data)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'User registration was successful')

    def test_create_user_view_invalid_data(self):
        self.user_data['password2'] = 'wrongpassword'
        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'The entered passwords do not match.')
        self.assertEqual(User.objects.count(), 0)

    def test_create_user_view_short_password(self):
        self.user_data['password1'] = 'pw'
        self.user_data['password2'] = 'pw'
        response = self.client.post(self.url, self.user_data)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'The password entered is too short.')
        self.assertEqual(User.objects.count(), 0)


class UserUpdateViewTestCase(TestCase):
    """Tests for UserUpdateView view."""

    fixtures = ['users.json']

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.form_data = valid_form.copy()
        self.client = Client()
        self.client.force_login(self.user1)

    def test_user_update_unauthenticated_user(self):
        self.client.logout()
        response = self.client.get(reverse('update_user', args=[self.user1.pk]))
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            'You are not signed in! Please, sign in',
        )

    def test_user_update_authenticated_user(self):
        response = self.client.get(reverse('update_user', args=[self.user1.pk]))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/update_user.html')

    def test_user_update_view_with_invalid_user(self):
        response = self.client.get(
            reverse('update_user', args=[self.user2.pk]),
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('user_list'))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You don't have the rights to modify another user.",
        )

    def test_user_update_view_with_valid_form(self):
        response = self.client.post(
            reverse('update_user', args=[self.user1.pk]),
            data=self.form_data,
        )
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('user_list'))
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, 'John')
        self.assertEqual(self.user1.last_name, 'Doe')
        self.assertEqual(self.user1.username, 'johndoe')
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "The user has been successfully updated",
        )

    def test_user_update_view_with_invalid_form(self):
        invalid_form_data = self.form_data.copy()
        invalid_form_data['password2'] = 'invalidpass'

        response = self.client.post(
            reverse('update_user', args=[self.user1.pk]),
            data=invalid_form_data,
        )

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/update_user.html')
        self.user1.refresh_from_db()
        self.assertFalse(self.user1.check_password('invalidpass'))


class UserDeleteViewTest(TestCase):
    """Tests for UserDeleteView view."""

    fixtures = ['users.json']

    def setUp(self):
        self.user1 = User.objects.get(pk=1)
        self.user2 = User.objects.get(pk=2)
        self.url = reverse('delete_user', kwargs={'pk': self.user1.pk})
        self.login_url = reverse('login')
        self.user_list_url = reverse('user_list')

    def test_delete_user_view_unauthenticated_user(self):
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, f"{self.login_url}")
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You are not signed in! Please, sign in.",
        )

    def test_delete_authenticated_user_not_owner(self):
        self.client.force_login(self.user2)
        response = self.client.get(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, self.user_list_url)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You don't have the rights to modify another user.",
        )

    def test_delete_authenticated_user_owner(self):
        self.client.force_login(self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(self.url)
        messages = list(get_messages(response.wsgi_request))

        self.assertRedirects(response, self.user_list_url)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The user was successfuly deleted")
        self.assertFalse(User.objects.filter(pk=self.user1.pk).exists())
