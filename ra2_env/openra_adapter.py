from __future__ import annotations

from typing import Any, Optional


class OpenRAAdapter:
    """Minimal adapter for a real OpenRA/OpenEnv runtime.

    This sits between the local Gymnasium environment and the external runtime,
    and is intentionally small and explicit for the current Phase 1 work.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self._client = None

    def connect(self):
        try:
            from openra_env.client import OpenRAEnv
        except ImportError as exc:  # pragma: no cover - real runtime dependency
            raise RuntimeError(
                "OpenRA runtime dependency is not installed. Install the OpenRA environment "
                "support before connecting to the live server."
            ) from exc

        self._client = OpenRAEnv(base_url=self.base_url)
        return self._client

    async def reset(self):
        if self._client is None:
            self.connect()
        return await self._client.reset()

    async def step(self, action: Any):
        if self._client is None:
            self.connect()
        return await self._client.step(action)

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._client = None
