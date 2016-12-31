import typing

from django.db import connection
from django.http import JsonResponse
from django.views import View


class ApiView(View):

    @staticmethod
    def response(data: dict={}, status_code: int=200,
                 message: typing.Union[str, None]=None) -> JsonResponse:
        payload = {
            'status': 'success' if status_code < 400 else 'error',
            'data': data,
            'message': message
        }
        response = JsonResponse(payload)
        response.status_code = status_code
        return response


class PingView(ApiView):

    def get(self, request) -> JsonResponse:
        cursor = connection.cursor()
        cursor.execute('''SELECT 1''')
        assert cursor.fetchone()[0] == 1
        return self.response(message="PONG")
