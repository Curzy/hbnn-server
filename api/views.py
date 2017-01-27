"""
    API
    ~~~~~~~~~
"""

import json
import typing
import uuid

from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection
from django.http import JsonResponse, QueryDict
from django.views import View

from api.decorators import jwt_login_required
from user.models import User, UserProfile
from utils.auth import JWTManager


class APIView(View):
    """혼밥남녀 API는 이 APIView를 상속받아 json 포맷으로 응답합니다
    """

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
    """서버에 ping을 보내어 라이브 상태를 확인합니다"""

    def get(self, request) -> JsonResponse:
        """

        :param request:
        :return:
        예:
            request: /api/ping/
            method: GET
            response: {
                'status': 'success',
                'data': None,
                'message': 'PONG'
            }
        """
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


class UserProfileAPIView(APIView):
    def get_user(self, user_id):
        try:
            user = User.objects.get(id=user_id)
        except ObjectDoesNotExist:
            return self.response(status_code=404,
                                 message='User does not exist')
        return user

    @jwt_login_required
    def post(self, request, user_id: uuid.UUID) -> JsonResponse:
        user = self.get_user(user_id)

        taste = request.POST.get('taste')
        introduction = request.POST.get('introduction')
        description = request.POST.get('description')

        userprofile = UserProfile.objects.create(
            user=user,
            taste=taste,
            introduction=introduction,
            description=description
        )

        serialized_userprofile = \
            self.serialize_userprofiles(profile=[userprofile, ])[0]
        return self.response(data=serialized_userprofile)

    @jwt_login_required
    def get(self, request, user_id: uuid.UUID) -> JsonResponse:
        user = self.get_user(user_id)

        try:
            userprofile = user.userprofile
        except AttributeError:
            return self.response(status_code=404,
                                 message='User profile does not exist')

        serialized_userprofile = \
            self.serialize_userprofiles(profile=[userprofile, ])[0]
        return self.response(data=serialized_userprofile)

    @jwt_login_required
    def put(self, request, user_id: uuid.UUID) -> JsonResponse:
        user = self.get_user(user_id)
        try:
            userprofile = user.userprofile
        except AttributeError:
            return self.response(status_code=404,
                                 message='User profile does not exist')

        parameters = QueryDict(request.body)
        for field in parameters:
            try:
                setattr(userprofile, field, parameters.get(field))
                userprofile.save()
            except AttributeError:
                'error'
        userprofile.refresh_from_db()

        serialized_userprofile = \
            self.serialize_userprofiles(profile=[userprofile, ])[0]
        return self.response(data=serialized_userprofile)

    @staticmethod
    def serialize_userprofiles(profile):
        dump = serializers.serialize(
            'json', profile,
            fields=('user', 'taste', 'introduction', 'description')
        )
        return json.loads(dump)
