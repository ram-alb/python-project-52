from http import HTTPStatus

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import Client, TestCase
from django.urls import reverse

user1_pk = 17
user2_pk = 18
passw = 'qwe'

valid_form = {
    'first_name': 'John',
    'last_name': 'Doe',
    'username': 'johndoe',
    'password1': 'password',
    'password2': 'password',
}


class CreateUserViewTestCase(TestCase):
    """Tests for the CreateUserView view."""

    def setUp(self):
        """Set up the test environment."""
        self.url = reverse('create_user')
        self.user_data = valid_form.copy()

    def test_create_user_view_exists(self):
        """Test that the CreateUserView view exists."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_user_view_valid_data(self):
        """Test that the CreateUserView view creates a user with valid data."""
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(User.objects.count(), 1)

    def test_create_user_view_invalid_data(self):
        """Test that a user with invalid data will not be created."""
        self.user_data['password2'] = 'wrongpassword'
        response = self.client.post(self.url, self.user_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertContains(response, 'The entered passwords do not match.')
        self.assertEqual(User.objects.count(), 0)

    def test_create_user_view_short_password(self):
        """Test that a user will not be created with a short password."""
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
        """Set up the test environment."""
        self.client = Client()

        self.user = User.objects.get(pk=user1_pk)
        self.user2 = User.objects.get(pk=user2_pk)

        # login the test user
        self.client.login(
            username=self.user.username,
            password=passw,
        )

        # create a form to update the user's information
        self.form_data = valid_form.copy()

    def test_user_update_view(self):
        """Test that the user update page is accessible."""
        response = self.client.get(reverse('update_user', args=[self.user.pk]))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/update_user.html')

    def test_user_update_view_with_invalid_user(self):
        """Test that a user cannot edit another user's profile."""
        response = self.client.get(
            reverse('update_user', args=[self.user2.pk]),
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('user_list'))

    def test_user_update_view_with_valid_form(self):
        """Test that a user can update their profile with a valid form."""
        response = self.client.post(
            reverse('update_user', args=[self.user.pk]),
            data=self.form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse('user_list'))

        # check that the user's information has been updated in the database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.last_name, 'Doe')
        self.assertEqual(self.user.username, 'johndoe')

        # check that the user's password has been changed
        self.assertTrue(self.user.check_password('password'))

    def test_user_update_view_with_invalid_form(self):
        """Test that a user cannot update their profile with an invalid form."""
        invalid_form_data = self.form_data.copy()
        invalid_form_data['password2'] = 'invalidpass'

        response = self.client.post(
            reverse('update_user', args=[self.user.pk]),
            data=invalid_form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, 'users/update_user.html')

        # check that the user's information has not been updated in the database
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.first_name, 'John')
        self.assertNotEqual(self.user.last_name, 'Doe')
        self.assertNotEqual(self.user.username, 'newtestuser')

        # check that the user's password has not been changed
        self.assertFalse(self.user.check_password('invalidpass'))


class UserDeleteViewTest(TestCase):
    """Tests for UserDeleteView view."""

    fixtures = ['users.json']

    def setUp(self):
        """Set up the test environment."""
        self.user = User.objects.get(pk=user1_pk)
        self.user2 = User.objects.get(pk=user2_pk)
        self.url = reverse('delete_user', kwargs={'pk': self.user.pk})
        self.login_url = reverse('login')
        self.user_list_url = reverse('user_list')

    def test_delete_user_view_unauthenticated_user(self):
        """Test when a user is unuathenticated."""
        response = self.client.get(self.url)
        self.assertRedirects(response, f"{self.login_url}")
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You are not signed in! Please, sign in.",
        )

    def test_delete_authenticated_user_not_owner(self):
        """Test when user try to delete another user profile."""
        self.client.login(username=self.user2.username, password=passw)
        response = self.client.get(self.url)
        self.assertRedirects(response, self.user_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]),
            "You don't have the rights to modify another user.",
        )

    def test_delete_authenticated_user_owner(self):
        """Test when user delete own profile."""
        self.client.login(username=self.user.username, password=passw)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        response = self.client.post(self.url)
        self.assertRedirects(response, self.user_list_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "The user was successfuly deleted")

        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())
