import uuid

from django.test import TestCase, LiveServerTestCase
from django.urls import reverse
from urllib.parse import urljoin, urlencode

from .models import HBNNUser


class HBBNUserTestCase(TestCase):

    def test_user_create(self):
        email = 'test@test.com'
        username = 'test'
        password = 'test'

        HBNNUser.objects.create_user(email,
                                     username,
                                     password)
        user = HBNNUser.objects.get(email=email)

        self.assertTrue(isinstance(user.id, uuid.UUID))
        self.assertEqual(user.email, email)
        self.assertEqual(user.username, username)
        self.assertTrue(user.check_password(password))

        modified_username = 'test2'
        user.username = modified_username
        user.save()

        self.assertNotEqual(user.created_at, user.modified_at)


class HBNNUserAPITestCase(LiveServerTestCase):
    url = reverse('user_api')

    email = 'test@test.com'
    username = 'test'
    password = 'test'

    def test_api_user_create(self):
        url = self.url

        email = self.email
        username = self.username
        password = self.password

        response = self.client.post(url,
                                    {
                                        'email': email,
                                        'username': username,
                                        'password': password
                                    })

        self.assertEqual(response.json().get('status'), 'success')
        data = response.json().get('data')
        self.assertEqual(data.get('email'), email)
        self.assertEqual(data.get('username'), username)

    def test_api_user_read_all(self):
        url = self.url

        response = self.client.get(url)
        self.assertEqual(
            response.json(),
            {
                'status': 'success',
                'data': [],
                'message': None
            }
        )

    def test_api_user_read_by_uuid(self):
        url = HBNNUserAPITestCase.url

        email = self.email
        username = self.username
        password = self.password

        HBNNUser.objects.create_user(email,
                                     username,
                                     password)
        user = HBNNUser.objects.get(email=email)
        user_id = str(user.id)

        response = self.client.get(urljoin(url, '/'.join([user_id, ''])))
        self.assertEqual(response.json().get('status'), 'success')
        data = response.json().get('data')
        self.assertEqual(data.get('email'), email)
        self.assertEqual(data.get('username'), username)
        self.assertEqual(data.get('id'), user_id)

    def test_api_user_update(self):
        url = self.url

        email = self.email
        username = self.username
        password = self.password

        new_username = 'test2'
        new_password = 'test2'
        HBNNUser.objects.create_user(email,
                                     username,
                                     password)
        user = HBNNUser.objects.get(email=email)
        user_id = str(user.id)

        parameter = {
            'username': new_username,
            'password': new_password
        }
        response = self.client.put(urljoin(url, '/'.join([user_id, ''])),
                                   data=urlencode(parameter))
        self.assertEqual(response.json().get('status'), 'success')
        data = response.json().get('data')
        self.assertEqual(data.get('email'), email)
        self.assertEqual(data.get('username'), new_username)
        self.assertEqual(data.get('id'), user_id)
        user = HBNNUser.objects.get(email=email)
        self.assertTrue(user.check_password(new_password))

    def test_api_user_delete(self):
        url = self.url

        email = self.email
        username = self.username
        password = self.password

        HBNNUser.objects.create_user(email,
                                     username,
                                     password)
        user = HBNNUser.objects.get(email=email)
        user_id = str(user.id)

        response = self.client.delete(urljoin(url, '/'.join([user_id, ''])))
        self.assertEqual(0, HBNNUser.objects.filter(id=user_id).count())
        self.assertEqual(response.json().get('message'),
                         'Successfully deleted')
