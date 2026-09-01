from __future__ import annotations

import asyncio
import threading
from typing import Any, Optional


class RuntimeClientBridge:
    """Bridge from an async OpenEnv client into the synchronous Gymnasium API.

    This keeps the environment logic stable while allowing a real OpenRA/OpenEnv
    client to be injected later.
    """

    def __init__(self, factory: Optional[Any] = None, *, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.factory = factory
        self._loop = None
        self._thread = None
        self._client = None
        self._lock = threading.Lock()

        if self.factory is not None:
            self._client = self.factory(base_url=self.base_url)

    def start(self):
        if self._thread is not None and self._thread.is_alive():
            return self._client

        def _runner():
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
            if self.factory is not None and self._client is None:
                self._client = self.factory(base_url=self.base_url)
            self._loop.run_forever()

        self._thread = threading.Thread(target=_runner, daemon=True)
        self._thread.start()
        return self._client

    def close(self):
        if self._loop is not None:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None
            self._client = None

    def call_soon(self, coro):
        if self._loop is None:
            raise RuntimeError("Runtime bridge has not been started.")
        future = asyncio.run_coroutine_threadsafe(coro, self._loop)
        return future.result(timeout=60.0)
