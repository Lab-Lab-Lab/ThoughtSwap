import os
from pathlib import Path
from django.core.asgi import get_asgi_application # num 1 of 4ish that have to 
# be in the correct order https://forum.djangoproject.com/t/i-get-the-error-apps-arent-loaded-yet-when-publishing-with-daphne/30320/14
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
# thoughtswap/
APPS_DIR = BASE_DIR / "thoughtswap"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

sett = env("DJANGO_SETTINGS_MODULE")
print("DJANGO_SETTINGS_MODULE before setting in asgi", sett)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thoughtswap.settings")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", sett) # num2

django_asgi_app = get_asgi_application() # num 3

from thoughtswap.thoughtswap.routing import websocket_urlpatterns # 4a
from thoughtswap.chat.routing import websocket_urlpatterns as thoughtswap_chat_routing #4b



application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(websocket_urlpatterns + thoughtswap_chat_routing)
            )
        ),
    }
)
