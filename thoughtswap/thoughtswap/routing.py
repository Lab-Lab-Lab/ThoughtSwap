from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/thoughtswap/(?P<course_code>\w+)/$",
        consumers.ThoughtSwapConsumer.as_asgi(),
    ),
]
