# https://realpython.com/getting-started-with-django-channels/
# from channels.routing import route
# from appmain.consumers import ws_connect, ws_disconnect

# channel_routing = [
#     route('websocket.connect', ws_connect),
#     route('websocket.disconnect', ws_disconnect),
# ]

# mysite/routing.py
# https://channels.readthedocs.io/en/latest/tutorial/part_2.html
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})