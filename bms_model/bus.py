from collections import defaultdict, deque
from typing import Dict, Deque, List, Iterable, Any

class MessageBus:
    """A minimal in-process pub/sub message bus."""
    def __init__(self):
        self._subs: Dict[str, List[str]] = defaultdict(list)
        self._queues: Dict[str, Deque[dict]] = defaultdict(deque)

    def subscribe(self, topic: str, agent_id: str):
        if agent_id not in self._subs[topic]:
            self._subs[topic].append(agent_id)

    def publish(self, topic: str, message: dict):
        self._queues[topic].append(message)

    def drain(self, topic: str) -> Iterable[dict]:
        q = self._queues[topic]
        while q:
            yield q.popleft()
