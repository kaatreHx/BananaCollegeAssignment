from django.urls import path

from .views import event_stream

urlpatterns = [
    path("stream/", event_stream, name="event-stream"),
]
