from functools import wraps

from django.utils.decorators import available_attrs

from utils.auth import JWTManager


def jwt_login_required(view_func):
    """JWT(Json Web Token)을 통한 인증이 필요한 경우에 사용합니다"""
    def fail():
        from api.views import APIView
        return APIView.response(status_code=401, message='JWT required')

    def decorator(view_func_):
        @wraps(view_func_, assigned=available_attrs(view_func_))
        def _wrapped_view(view, *args, **kwargs):
            authorization = view.request.META.get('HTTP_AUTHORIZATION')
            if authorization is None:
                return fail()
            auth_options = authorization.split(' ')
            if len(auth_options) != 2:
                return fail()
            type_, token = auth_options
            if type_.upper() != 'JWT':
                return fail()
            user = JWTManager.decode(token=token)
            if user is None:
                return fail()
            view.request.user = user
            return view_func_(view, *args, **kwargs)

        return _wrapped_view

    return decorator(view_func)
