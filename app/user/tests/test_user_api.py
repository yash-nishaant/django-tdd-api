from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    # Helper function to create new user
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    # Test the user public API

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        # test creating user with valid payload is successful
        payload = {
            'email': 'test@gmail.com',
            'password': 'test',
            'name': 'Test Name'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exists(self):
        # test creating duplicate user fails
        payload = {'email': 'test@gmail.com', 'password': 'test'}
        create_user(**payload)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        # Test that password must be more than 6 characters
        payload = {'email': 'test@londonappdev.com', 'password': 'pw'}
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_creat_token_for_user(self):
        # Test that token is created for user
        payload = {'email': 'test@gmail.com', 'password': 'test'}
        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_token_invalid_credentials(self):
        # Test that token is not created for invalid credentials
        create_user(email='test@gmail.com', password='test')
        payload = {'email': 'test@gmail.com', 'password': 'nottest'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        # TEst that token is not created for non-existent user
        payload = {'email': 'test@gmail.com', 'password': 'test'}
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_missing_field(self):
        # Test that email and password are required
        res = self.client.post(TOKEN_URL, {'email': 'one', 'password': ''})
        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
