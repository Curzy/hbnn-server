import typing
from datetime import datetime, timedelta

import jwt
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from jwt import DecodeError

from user.models import User


class JWTManager:
    @staticmethod
    def encode(user_id: str) -> str:
        """
        :return: JSON Web Token String
        """
        # 브루트포싱 방지를 위한 자체 유효성 체크
        utcnow = int(datetime.utcnow().timestamp())
        seconds_of_a_day = int(timedelta(days=1).total_seconds())
        payload = {
            'user_id': user_id,
            'utcnow': utcnow,
            'a_day_ago': utcnow - seconds_of_a_day,
        }
        token = jwt.encode(payload=payload, key=settings.SECRET_KEY,
                           algorithm='HS256')
        return token.decode('utf8')

    @staticmethod
    def decode(token: str) -> typing.Optional[User]:
        """
        :return: User.id
        """
        seconds_of_a_day = int(timedelta(days=1).total_seconds())
        try:
            data = jwt.decode(jwt=token, key=settings.SECRET_KEY, verify=False,
                              algorithm='HS256')
        except DecodeError:
            return None
        # 키 체크
        for k in ('utcnow', 'a_day_ago', 'user_id'):
            if k not in data:
                return None
        # 유효성 체크
        if seconds_of_a_day != data['utcnow'] - data['a_day_ago']:
            return None

        try:
            return User.objects.get(id=data['user_id'])
        except ObjectDoesNotExist:
            return None
