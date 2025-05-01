from collections import defaultdict
from typing import Callable, Any
from .events import Event

class EventBus:
    def __init__(self):
        self._subscribers: dict[Event, list[Callable[..., Any]]] = defaultdict(list)

    def subscribe(self, event: Event, handler: Callable[..., Any]) -> None:
        self._subscribers[event].append(handler)
    
    def publish(self, event:Event, *args, **kw) -> None:
        for handler in self._subscribers.get(event, ()):
            handler(*args, **kw)