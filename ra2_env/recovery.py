from __future__ import annotations

from typing import Any

import numpy as np


class SupervisedEnv:
    """Minimal wrapper that enforces a stable step/reset lifecycle.

    It intentionally does not replace the inner environment semantics; it only
    stabilizes calls and keeps a consistent return structure for local tests.
    """

    def __init__(self, env: Any):
        self.env = env

    def reset(self, *, seed: int | None = None, options: dict | None = None):
        obs, info = self.env.reset(seed=seed, options=options)
        if isinstance(obs, list):
            obs = np.asarray(obs, dtype=np.float32)
        return obs.astype(np.float32), info

    def step(self, action: Any):
        obs, reward, terminated, truncated, info = self.env.step(action)
        if isinstance(obs, list):
            obs = np.asarray(obs, dtype=np.float32)
        return obs.astype(np.float32), reward, terminated, truncated, info

    def close(self):
        return self.env.close()
