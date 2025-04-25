import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from thoughtswap.thoughtswap.routing import websocket_urlpatterns
from thoughtswap.chat.routing import websocket_urlpatterns as thoughtswap_chat_routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thoughtswap.settings")

django_asgi_app = get_asgi_application()


application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns+thoughtswap_chat_routing))
        ),
    }
)
