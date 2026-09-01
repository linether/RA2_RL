from __future__ import annotations

import pytest

from ra2_env.runtime_adapter import RuntimeClientBridge


@pytest.mark.unit
class TestRuntimeClientBridge:
    def test_bridge_starts_and_closes_cleanly(self):
        class DummyClient:
            def __init__(self, *, base_url):
                self.base_url = base_url

        bridge = RuntimeClientBridge(factory=DummyClient, base_url="http://localhost:8000")
        client = bridge.start()
        assert client is not None
        assert client.base_url == "http://localhost:8000"
        bridge.close()

    def test_bridge_rejects_unstarted_call(self):
        bridge = RuntimeClientBridge()

        async def _dummy():
            return True

        coro = _dummy()
        try:
            with pytest.raises(RuntimeError, match="started"):
                bridge.call_soon(coro)
        finally:
            coro.close()
