from __future__ import annotations

import numpy as np
import pytest
from gymnasium import spaces

from ra2_env import RA2Env


class _MockClient:
    def __init__(self):
        self.reset_calls = 0
        self.step_calls = 0

    def reset(self, *, seed=None, options=None):
        self.reset_calls += 1
        obs = np.array([0.0, 0.0, float(self.reset_calls)], dtype=np.float32)
        return obs, {
            "reset_calls": self.reset_calls,
            "seed": seed,
            "status": "ok",
        }

    def step(self, action):
        self.step_calls += 1
        if not isinstance(action, (int, np.integer)):
            raise ValueError("action must be an integer action id")
        if action < 0 or action >= 4:
            raise ValueError("action id out of range for the minimal discrete space")

        obs = np.array([1.0, float(action), float(self.step_calls)], dtype=np.float32)
        return obs, 1.0, False, False, {"step_calls": self.step_calls, "action": int(action)}


def _make_env(max_episode_steps: int = 8):
    env = RA2Env(base_url="http://example.invalid:8000", max_episode_steps=max_episode_steps)
    env._client = _MockClient()
    env._connected = True
    return env


@pytest.mark.unit
class TestRA2EnvConstructor:
    def test_constructor_sets_minimal_public_contract(self):
        env = RA2Env(base_url="http://example.invalid:8000", max_episode_steps=7)

        assert env.base_url == "http://example.invalid:8000"
        assert env.max_episode_steps == 7
        assert isinstance(env.action_space, spaces.Space)
        assert isinstance(env.observation_space, spaces.Space)
        assert hasattr(env, "metadata")


@pytest.mark.unit
class TestRA2EnvResetStep:
    def test_reset_returns_observation_and_info_tuple(self):
        env = _make_env()

        obs, info = env.reset(seed=7)

        assert isinstance(obs, np.ndarray)
        assert isinstance(info, dict)
        assert "reset_calls" in info
        assert info["seed"] == 7

    def test_step_returns_five_tuple_in_gymnasium_order(self):
        env = _make_env()
        env.reset(seed=11)

        result = env.step(1)

        assert isinstance(result, tuple)
        assert len(result) == 5

        obs, reward, terminated, truncated, info = result

        assert isinstance(obs, np.ndarray)
        assert isinstance(reward, (int, float, np.floating))
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert isinstance(info, dict)
        assert info["action"] == 1

    def test_reset_without_server_raises_clear_error(self):
        env = RA2Env(base_url="http://example.invalid:8000", max_episode_steps=4)
        env._connected = False
        env._client = None

        with pytest.raises((ConnectionError, RuntimeError, OSError), match=r"server|openra|localhost|8000"):
            env.reset()


@pytest.mark.unit
class TestRA2EnvErrorHandling:
    def test_invalid_action_id_is_rejected(self):
        env = _make_env()
        env.reset()

        with pytest.raises((ValueError, AssertionError), match=r"action|range|invalid"):
            env.step(99)

    def test_closed_env_rejects_subsequent_calls(self):
        env = _make_env()
        env.reset()
        env.close()

        with pytest.raises((RuntimeError, ValueError), match=r"closed|close|Cannot"):
            env.step(0)
