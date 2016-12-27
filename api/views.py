import typing

from django.http import JsonResponse
from django.views import View


class ApiView(View):

    @staticmethod
    def response(data: dict={}, status_code: int=200, message: typing.Union[str, None]=None) -> JsonResponse:
        payload = {
            'status': 'success' if status_code < 400 else 'error',
            'data': data,
            'message': message
        }
        response = JsonResponse(payload)
        response.status_code = status_code
        return response

