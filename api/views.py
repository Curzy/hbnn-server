import json
import typing
import uuid

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.http import JsonResponse, QueryDict
from django.views import View

from api.decorators import jwt_login_required
from user.models import User
from utils.auth import JWTManager


class APIView(View):
    @staticmethod
    def response(data: typing.Optional[typing.Union[dict, list]] = None,
                 status_code: int = 200,
                 message: typing.Optional[str] = None) -> JsonResponse:
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
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        if User.objects.filter(
                email=User.objects.normalize_email(email)).exists():
            return self.response(status_code=404,
                                 message='Email already exists')
        user = User.objects.create_user(email,
                                        username,
                                        password)

        serialized_user_data = self.serialize_users([user, ])[0]
        return self.response(data=serialized_user_data)

    def get(self, request, user_id: uuid.UUID = None) -> JsonResponse:
        if user_id:
            try:
                user = User.objects.get(id=user_id)
            except ObjectDoesNotExist:
                return self.response(status_code=404,
                                     message='User does not exist')
            serialized_user_data = self.serialize_users([user, ])[0]
        else:
            users = User.objects.all()
            serialized_user_data = self.serialize_users(users)

        return self.response(data=serialized_user_data)

    @jwt_login_required
    def put(self, request, user_id: uuid.UUID) -> JsonResponse:
        if user_id == request.user.id:
            return self.response(status_code=401,
                                 message='Unauthorized')
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return self.response(status_code=404,
                                 message='User does not exist')

        parameters = QueryDict(request.body)
        new_username = parameters.get('username')
        new_password = parameters.get('password')

        if new_username:
            user.username = new_username
        if new_password:
            user.set_password(new_password)

        user.save()

        serialized_user_data = self.serialize_users([user, ])[0]
        return self.response(data=serialized_user_data)

    @jwt_login_required
    def delete(self, request, user_id: uuid.UUID) -> JsonResponse:
        if user_id == request.user.id:
            return self.response(status_code=401, message='Unauthorized')

        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return self.response(status_code=404,
                                 message='User does not exist')

        user.delete()
        return self.response(data={}, message='Successfully deleted')

    @staticmethod
    def serialize_users(data):
        dump = serializers.serialize(
            'json', data,
            fields=('username', 'email', 'created_at')
        )
        return json.loads(dump)


class JWTAuthView(APIView):
    def post(self, request) -> JsonResponse:
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            return self.response(status_code=400,
                                 message='User does not exist')
        if not user.check_password(raw_password=password):
            return self.response(status_code=400,
                                 message='User does not exist')
        token = JWTManager.encode(user_id=str(user.id))
        data = {'token': token}
        return self.response(data=data)
