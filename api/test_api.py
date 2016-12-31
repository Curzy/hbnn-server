import json

from django.test import LiveServerTestCase, TestCase
from django.urls import reverse

from .views import ApiView


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
            response = ApiView.response(*args)
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
                'data': {},
                'message': 'PONG'
            }
        )
        self.assertEqual(response.status_code, 200)
