import asyncio
from datetime import datetime
from typing import Callable, Any


class EventBus:
    _instance: "EventBus | None" = None

    def __new__(cls) -> "EventBus":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._listeners: dict[str, list[Callable]] = {}
            cls._instance._log_queue: asyncio.Queue = asyncio.Queue()
        return cls._instance

    def subscribe(self, event: str, callback: Callable) -> None:
        self._listeners.setdefault(event, []).append(callback)

    async def emit(self, event: str, tag: str, message: str, **kwargs: Any) -> None:
        timestamp = datetime.utcnow().strftime("%H:%M:%S")
        log_entry = {
            "timestamp": timestamp,
            "event": event,
            "tag": tag,
            "message": message,
            **kwargs,
        }
        await self._log_queue.put(log_entry)
        for callback in self._listeners.get(event, []):
            if asyncio.iscoroutinefunction(callback):
                await callback(log_entry)
            else:
                callback(log_entry)

    async def get_log(self) -> dict | None:
        try:
            return self._log_queue.get_nowait()
        except asyncio.QueueEmpty:
            return None

    async def drain_logs(self) -> list[dict]:
        logs = []
        while not self._log_queue.empty():
            logs.append(self._log_queue.get_nowait())
        return logs
