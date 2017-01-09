from django.conf.urls import url

from .views import HBNNUserAPIView


urlpatterns = [
    url(r'^$', HBNNUserAPIView.as_view(), name='user_api'),
    url(r'^([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$',
        HBNNUserAPIView.as_view(), name='user_api'),
]
