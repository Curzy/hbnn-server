import json
from urllib.parse import urljoin, urlencode

from django.test import LiveServerTestCase, TestCase
from django.urls import reverse

from user.models import User, UserProfile
from api.views import APIView


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


class HBNNLiveServerTestCase(LiveServerTestCase):
    email = 'test@test.com'
    username = 'test'
    password = 'test'
    taste = UserProfile.KOREAN
    introduction = '안녕하세요'
    description = '자세한 설명은 생략한다'

    def create_user(self):
        url = reverse('api_user')
        self.client.post(url, {
            'email': self.email,
            'username': self.username,
            'password': self.password,
        })

    def get_jwt_token(self):
        response = self.client.post(reverse('api_auth'), {
            'email': self.email,
            'password': self.password,
        })
        token = f"JWT {response.json()['data']['token']}"
        return token


class UserAPITestCase(HBNNLiveServerTestCase):
    url = reverse('api_user')

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
        fields = data.get('fields')
        self.assertEqual(fields.get('email'), email)
        self.assertEqual(fields.get('username'), username)

        fail_response = self.client.post(url,
                                         {
                                             'email': email,
                                             'username': username,
                                             'password': password
                                         })
        self.assertEqual(fail_response.json().get('status'), 'error')

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

        self.create_user()
        user = User.objects.get(email=self.email)
        user_id = str(user.id)

        url = urljoin(base_url, f'{user_id}/')

        response = self.client.get(url)
        self.assertEqual(response.json().get('status'), 'success')
        data = response.json().get('data')
        pk = data.get('pk')
        self.assertEqual(pk, user_id)
        fields = data.get('fields')
        self.assertEqual(fields.get('email'), self.email)
        self.assertEqual(fields.get('username'), self.username)

        false_uuid = '00000000-0000-0000-0000-000000000000'
        false_uuid_url = urljoin(base_url, f'{false_uuid}/')
        fail_response = self.client.get(false_uuid_url)
        self.assertEqual(fail_response.json().get('status'), 'error')

    def test_api_user_update(self):
        base_url = self.url
        self.create_user()
        user = User.objects.get(email=self.email)
        user_id = str(user.id)

        url = urljoin(base_url, f'{user_id}/')

        new_username = 'test2'
        new_password = 'test2'

        parameter = {
            'username': new_username,
            'password': new_password
        }

        # Get jwt token
        token = self.get_jwt_token()

        # Authorization failure
        response = self.client.put(url, data=urlencode(parameter))
        self.assertEqual(response.json().get('status'), 'error')

        # Authorization success
        response = self.client.put(url, data=urlencode(parameter),
                                   HTTP_AUTHORIZATION=token)
        self.assertEqual(response.json().get('status'), 'success')
        data = response.json().get('data')
        pk = data.get('pk')
        self.assertEqual(pk, user_id)
        fields = data.get('fields')
        self.assertEqual(fields.get('email'), self.email)
        self.assertEqual(fields.get('username'), new_username)
        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

        false_uuid = '00000000-0000-0000-0000-000000000000'
        false_uuid_url = urljoin(base_url, f'{false_uuid}/')
        fail_response = self.client.put(false_uuid_url,
                                        data=urlencode(parameter))
        self.assertEqual(fail_response.json().get('status'), 'error')

    def test_api_user_delete(self):
        base_url = self.url

        self.create_user()
        user = User.objects.get(email=self.email)
        user_id = str(user.id)

        token = self.get_jwt_token()

        url = urljoin(base_url, f'{user_id}/')

        # Authorization failure
        response = self.client.delete(url)
        self.assertEqual(response.json().get('status'), 'error')

        # Authorization success
        response = self.client.delete(url, HTTP_AUTHORIZATION=token)
        self.assertEqual(response.json().get('status'), 'success')
        self.assertEqual(0, User.objects.filter(id=user_id).count())
        self.assertEqual(response.json().get('message'),
                         'Successfully deleted')

        false_uuid = '00000000-0000-0000-0000-000000000000'
        false_uuid_url = urljoin(base_url, f'{false_uuid}/')
        fail_response = self.client.delete(false_uuid_url)
        self.assertEqual(fail_response.json().get('status'), 'error')


class JWTAuthAPITestCase(HBNNLiveServerTestCase):
    url = reverse('api_auth')

    def test_api_jwt_auth(self):
        # Create base user
        self.create_user()

        # Email checking failure
        fail_response = self.client.post(self.url, {
            'email': f'{self.email}-fake',
            'password': self.password,
        })
        self.assertEqual(fail_response.json().get('status'), 'error')

        # Password checking failure
        fail_response = self.client.post(self.url, {
            'email': self.email,
            'password': f'{self.password}-fake',
        })
        self.assertEqual(fail_response.json().get('status'), 'error')

        # Success
        response = self.client.post(self.url, {
            'email': self.email,
            'password': self.password,
        })
        self.assertEqual(response.json().get('status'), 'success')


class UserProfileAPITestCase(HBNNLiveServerTestCase):
    url = reverse('api_user')

    def create_user_profile(self, user):
        UserProfile.objects.create(
            user=user,
            taste=self.taste,
            introduction=self.introduction,
            description=self.description
        )

    def get_url(self, user_id):
        url = urljoin(self.url, f'{user_id}/profile/')
        return url

    def test_userprofile_create(self):
        self.create_user()
        user = User.objects.get(email=self.email)
        user_id = str(user.id)
        token = self.get_jwt_token()

        url = self.get_url(user_id)
        parameters = {
            'taste': self.taste,
            'introduction': self.introduction,
            'description': self.description
        }
        response = self.client.post(url,
                                    parameters,
                                    HTTP_AUTHORIZATION=token)

        self.assertEqual(response.json().get('status'), 'success')
        fields = response.json()['data']['fields']
        self.assertEqual(fields.get('introduction'), self.introduction)
        self.assertEqual(fields.get('description'), self.description)

    def test_userprofile_read(self):
        self.create_user()
        user = User.objects.get(email=self.email)
        self.create_user_profile(user)
        user_id = str(user.id)
        token = self.get_jwt_token()

        url = self.get_url(user_id)
        response = self.client.get(url,
                                   HTTP_AUTHORIZATION=token)

        self.assertEqual(response.json().get('status'), 'success')
        fields = response.json()['data']['fields']
        self.assertEqual(fields.get('taste'), self.taste)
        self.assertEqual(fields.get('introduction'), self.introduction)
        self.assertEqual(fields.get('description'), self.description)

    def test_userprofile_update(self):
        self.create_user()
        user = User.objects.get(email=self.email)
        self.create_user_profile(user)
        user_id = str(user.id)
        token = self.get_jwt_token()

        new_taste = UserProfile.JAPANESE
        new_introduction = '안녕못하다'
        url = self.get_url(user_id)
        parameter = {
            'taste': new_taste,
            'introduction': new_introduction,
        }

        response = self.client.put(url, data=urlencode(parameter),
                                   HTTP_AUTHORIZATION=token)
        self.assertEqual(response.json().get('status'), 'success')
        fields = response.json()['data']['fields']
        self.assertEqual(fields.get('taste'), new_taste)
        self.assertEqual(fields.get('introduction'), new_introduction)
