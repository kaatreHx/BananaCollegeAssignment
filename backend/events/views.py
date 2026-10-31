"""SSE endpoint: GET /api/events/stream/ streams leaderboard updates.

Plain Django view (not DRF): EventSource asks for text/event-stream and DRF
would reply 406. A simple view sidesteps content negotiation entirely.
"""

import json
import queue
import time

from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET

from .broker import subscribe, unsubscribe

KEEPALIVE_SECONDS = 15


def _frame(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, separators=(',', ':'))}\n\n"


@require_GET
@csrf_exempt
def event_stream(request):
    """Public live feed; the browser opens it with EventSource."""
    channel = subscribe()

    def stream():
        try:
            yield _frame("connected", {"message": "live leaderboard updates"})
            yield ": keep-alive\n\n"
            while True:
                try:
                    message = channel.get(timeout=KEEPALIVE_SECONDS)
                except queue.Empty:
                    yield f": keep-alive {int(time.time())}\n\n"
                    continue
                yield _frame(message["topic"], message["data"])
        except GeneratorExit:
            return
        finally:
            unsubscribe(channel)

    response = StreamingHttpResponse(stream(), content_type="text/event-stream")
    response["Cache-Control"] = "no-cache, no-transform"
    response["X-Accel-Buffering"] = "no"
    return response
