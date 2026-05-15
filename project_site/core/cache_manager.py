import time
from typing import Any, Optional


class CacheManager:
    _instance: Optional["CacheManager"] = None

    def __new__(cls) -> "CacheManager":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._store: dict[str, dict[str, Any]] = {}
        return cls._instance

    def set(self, key: str, value: Any, ttl: int = 300) -> None:
        self._store[key] = {
            "value": value,
            "expires_at": time.time() + ttl,
        }

    def get(self, key: str) -> Optional[Any]:
        entry = self._store.get(key)
        if entry is None:
            return None
        if time.time() > entry["expires_at"]:
            del self._store[key]
            return None
        return entry["value"]

    def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    def all_keys(self) -> list[str]:
        now = time.time()
        expired = [k for k, v in self._store.items() if now > v["expires_at"]]
        for k in expired:
            del self._store[k]
        return list(self._store.keys())
