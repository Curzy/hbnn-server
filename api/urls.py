from django.conf.urls import url

from .views import PingView


urlpatterns = [
    url(r'^ping/$', PingView.as_view(), name='api_ping'),
]
