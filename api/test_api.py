import json

from django.test import LiveServerTestCase, TestCase
from django.urls import reverse
from urllib.parse import urljoin, urlencode

from .views import APIView
from user.models import HBNNUser


class ApiViewTestCase(TestCase):

    def test_response(self):
        test_cases = (
            (
                ({'hello': 'world'}, 200),
                {
                    'status': 'success',
                    'data': {'hello': 'world'},
                    'message': None
                }
            ),
            (
                ({'hello': 'world'}, 201),
                {
                    'status': 'success',
                    'data': {'hello': 'world'},
                    'message': None
                }
            ),
            (
                ({'hello': 'world'}, 401, 'T^T'),
                {
                    'status': 'error',
                    'data': {'hello': 'world'},
                    'message': 'T^T'
                }
            )
        )

        for case in test_cases:
            args, expect = case
            response = APIView.response(*args)
            self.assertEqual(json.loads(response.content), expect)

            status_code = args[1] \
                if len(args) >= 2 and isinstance(args[1], int) else 200
            self.assertEqual(response.status_code, status_code)


class PingViewTestCase(LiveServerTestCase):

    def test_get(self):
        url = reverse('api_ping')

        response = self.client.get(url)
        self.assertEqual(
            response.json(),
            {
                'status': 'success',
                'data': None,
                'message': 'PONG'
            }
        )
        self.assertEqual(response.status_code, 200)


class UserAPITestCase(LiveServerTestCase):
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
        base_url = self.url

        email = self.email
        username = self.username
        password = self.password

        HBNNUser.objects.create_user(email,
                                     username,
                                     password)
        user = HBNNUser.objects.get(email=email)
        user_id = str(user.id)

        url = urljoin(base_url, '/'.join([user_id, '']))

        response = self.client.get(url)
        self.assertEqual(response.json().get('status'), 'success')
        data = response.json().get('data')
        self.assertEqual(data.get('email'), email)
        self.assertEqual(data.get('username'), username)
        self.assertEqual(data.get('id'), user_id)

    def test_api_user_update(self):
        base_url = self.url

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

        url = urljoin(base_url, '/'.join([user_id, '']))

        parameter = {
            'username': new_username,
            'password': new_password
        }

        response = self.client.put(url,
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
