"""In-process pub/sub for live leaderboard events.

One queue per connected browser. When a game finishes, `broadcast()` hands the
message to every queue; the SSE view in views.py streams them out.
"""

import queue

_subscribers: list[queue.Queue] = []


def subscribe() -> queue.Queue:
    channel = queue.Queue(maxsize=100)
    _subscribers.append(channel)
    return channel


def unsubscribe(channel: queue.Queue) -> None:
    if channel in _subscribers:
        _subscribers.remove(channel)


def broadcast(topic: str, data: dict) -> None:
    for channel in list(_subscribers):
        try:
            channel.put_nowait({"topic": topic, "data": data})
        except queue.Full:
            pass
