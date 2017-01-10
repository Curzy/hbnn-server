import typing
import uuid

from django.db import connection
from django.http import JsonResponse, QueryDict
from django.views import View

from user.models import HBNNUser


class APIView(View):

    @staticmethod
    def response(data: typing.Union[dict, list]={}, status_code: int=200,
                 message: typing.Union[str, None]=None) -> JsonResponse:
        payload = {
            'status': 'success' if status_code < 400 else 'error',
            'data': data,
            'message': message
        }
        response = JsonResponse(payload)
        response.status_code = status_code
        return response


class PingView(APIView):

    def get(self, request) -> JsonResponse:
        cursor = connection.cursor()
        cursor.execute('''SELECT 1''')
        assert cursor.fetchone()[0] == 1
        return self.response(message="PONG")


class UserAPIView(APIView):

    def post(self, request) -> JsonResponse:
        try:
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
        except Exception as e:
            print(e)

        user = HBNNUser.objects.create_user(email,
                                            username,
                                            password)

        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

        return self.response(data=data)

    def get(self, request, user_id: uuid.UUID=None) -> JsonResponse:
        print(request.method)
        if user_id:
            user = HBNNUser.objects.get(id=user_id)
            data = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S')
            }

        else:
            users = HBNNUser.objects.values_list('id', 'username',
                                                 'email', 'created_at')
            data = [
                {
                    'id': id_,
                    'username': username,
                    'email': email,
                    'created_at': created_at.strftime('%Y-%m-%d %H:%M:%S')}
                for id_, username, email, created_at in users
            ]

        return self.response(data=data)

    def put(self, request, user_id: uuid.UUID) -> JsonResponse:
        user = HBNNUser.objects.get(id=user_id)

        parameters = QueryDict(request.body)
        new_username = parameters.get('username')
        new_password = parameters.get('password')

        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)

        user.save()

        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'created_at': user.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'modified_at': user.modified_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        return self.response(data=data)

    def delete(self, request, user_id: uuid.UUID) -> JsonResponse:
        user = HBNNUser.objects.get(id=user_id)

        user.delete()
        return self.response(data={}, message='Successfully deleted')
