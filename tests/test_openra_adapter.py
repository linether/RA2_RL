from __future__ import annotations

import pytest

from ra2_env.openra_adapter import OpenRAAdapter


@pytest.mark.unit
class TestOpenRAAdapter:
    def test_adapter_initializes_with_base_url(self):
        adapter = OpenRAAdapter(base_url="http://localhost:8000")
        assert adapter.base_url == "http://localhost:8000"
        assert adapter._client is None

    def test_adapter_raises_when_openra_package_missing(self, monkeypatch):
        def fail_import(*args, **kwargs):
            raise ImportError("missing")

        import builtins
        real_import = builtins.__import__

        def guarded_import(name, *rest, **kwargs):
            if name == "openra_env.client":
                raise ImportError("missing")
            return real_import(name, *rest, **kwargs)

        monkeypatch.setattr(builtins, "__import__", guarded_import)
        adapter = OpenRAAdapter()
        with pytest.raises(RuntimeError, match="OpenRA runtime dependency"):
            adapter.connect()
