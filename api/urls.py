from django.conf.urls import url

from .views import PingView, UserAPIView, JWTAuthView, UserProfileAPIView

urlpatterns = [
    url(r'^ping/$', PingView.as_view(), name='api_ping'),
    url(r'^users/$', UserAPIView.as_view(), name='api_user'),
    url((r'^users/'
         r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'),
        UserAPIView.as_view(), name='api_user'),
    url((r'^users/'
         r'([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/'
         r'profile/$'),
        UserProfileAPIView.as_view(), name='api_userprofile'),
    url(r'^auth/$', JWTAuthView.as_view(), name='api_auth'),
]
