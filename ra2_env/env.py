from __future__ import annotations

import threading
from typing import Any, Optional

import gymnasium as gym
import numpy as np


class RA2Env(gym.Env):
    """Minimal Gymnasium-compatible environment shell for Phase 1.

    This implementation is intentionally lightweight and local-first. It defines
    the public contract to be used by the project while keeping a path open for
    later integration with the OpenRA/OpenEnv client or the original-game bridge.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        observation_builder: Optional[Any] = None,
        action_mapper: Optional[Any] = None,
        reward_fn: Optional[Any] = None,
        max_episode_steps: int = 20000,
    ) -> None:
        self.base_url = base_url
        self.max_episode_steps = int(max_episode_steps)
        self.observation_builder = observation_builder
        self.action_mapper = action_mapper
        self.reward_fn = reward_fn

        self._closed = False
        self._connected = False
        self._client = None
        self._episode_steps = 0

        self.observation_space = gym.spaces.Box(
            low=-1e6,
            high=1e6,
            shape=(3,),
            dtype=np.float32,
        )
        self.action_space = gym.spaces.Discrete(4)

        self._lock = threading.RLock()

    def _ensure_connected(self) -> None:
        if self._closed:
            raise RuntimeError("RA2Env is closed and cannot be used.")
        if self._client is None:
            raise ConnectionError(
                "RA2Env is not connected to the runtime server. "
                "Start the local OpenRA/OpenEnv service or provide a mock client first."
            )
        self._connected = True

    def _validate_action(self, action: Any) -> int:
        if not isinstance(action, (int, np.integer)):
            raise ValueError(f"Action must be an integer action id, got {type(action)!r}")
        action_id = int(action)
        if action_id < 0 or action_id >= self.action_space.n:
            raise ValueError(
                f"Action id {action_id} is out of range for action space size {self.action_space.n}."
            )
        return action_id

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        self._ensure_connected()
        self._episode_steps = 0

        if self._client is not None:
            try:
                obs, info = self._client.reset(seed=seed, options=options)
            except TypeError:
                obs, info = self._client.reset()
        else:
            raise ConnectionError("No runtime client is available for reset().")

        if isinstance(obs, list):
            obs = np.asarray(obs, dtype=np.float32)
        elif not isinstance(obs, np.ndarray):
            obs = np.asarray(obs, dtype=np.float32)

        if info is None:
            info = {}
        if seed is not None:
            info["seed"] = seed
        return obs.astype(np.float32), info

    def step(self, action: Any):
        self._ensure_connected()
        action_id = self._validate_action(action)

        if self._client is None:
            raise ConnectionError("No runtime client is available for step().")

        try:
            raw = self._client.step(action_id)
        except TypeError:
            raw = self._client.step(action)

        if len(raw) != 5:
            raise ValueError(f"Client step() must return 5 values, got {len(raw)}.")

        obs, reward, terminated, truncated, info = raw
        if isinstance(obs, list):
            obs = np.asarray(obs, dtype=np.float32)
        elif not isinstance(obs, np.ndarray):
            obs = np.asarray(obs, dtype=np.float32)

        self._episode_steps += 1
        if self._episode_steps >= self.max_episode_steps:
            truncated = True

        if self._closed:
            raise RuntimeError("RA2Env is closed and cannot step again.")

        info = dict(info or {})
        info["action"] = action_id
        info["episode_steps"] = self._episode_steps
        info["max_episode_steps"] = self.max_episode_steps
        return obs.astype(np.float32), float(reward), bool(terminated), bool(truncated), info

    def close(self):
        with self._lock:
            self._closed = True
            self._connected = False
            self._client = None


__all__ = ["RA2Env"]
