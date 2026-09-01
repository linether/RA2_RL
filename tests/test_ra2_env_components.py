from __future__ import annotations

import numpy as np
import pytest

from ra2_env.action import DiscreteActionMapper
from ra2_env.observation import ObservationBuilder
from ra2_env.reward import RewardFunction
from ra2_env.recovery import SupervisedEnv


@pytest.mark.unit
class TestObservationBuilder:
    def test_build_returns_stable_vector(self):
        obs = {
            "tick": 42,
            "economy": {"cash": 3000, "power_provided": 200, "power_drained": 100},
            "units": [{"type": "e1"}, {"type": "1tnk"}],
            "buildings": [{"type": "fact"}],
            "visible_enemies": [{"type": "e1"}],
            "visible_enemy_buildings": [{"type": "powr"}],
            "result": "",
            "done": False,
        }

        builder = ObservationBuilder()
        vector = builder.build(obs)

        assert isinstance(vector, np.ndarray)
        assert vector.dtype == np.float32
        assert vector.shape == builder.space().shape
        assert np.isfinite(vector).all()
        assert vector[0] >= 0
        assert vector[3] >= 0

    def test_space_is_fixed_and_numeric(self):
        builder = ObservationBuilder()
        space = builder.space()
        assert space.shape == (10,)
        assert space.dtype == np.float32


@pytest.mark.unit
class TestActionMapper:
    def test_space_is_discrete_and_in_range(self):
        mapper = DiscreteActionMapper(n_actions=10)
        assert mapper.space().n == 10
        assert mapper.space().contains(0)
        assert mapper.space().contains(9)

    def test_commands_include_noop_and_actions(self):
        mapper = DiscreteActionMapper(n_actions=10)
        commands = mapper.commands(0, {})
        assert isinstance(commands, list)
        assert len(commands) >= 1
        assert commands[0]["action"] in {"noop", "harvest", "attack", "build"}

    def test_action_mask_defaults_to_all_available(self):
        mapper = DiscreteActionMapper(n_actions=10)
        mask = mapper.action_mask({})
        assert mask.shape == (10,)
        assert mask.dtype == np.float32
        assert mask.sum() == 10.0


@pytest.mark.unit
class TestRewardFunction:
    def test_reward_is_scalar_and_finite(self):
        fn = RewardFunction()
        obs = {"economy": {"cash": 5000}, "units": [{"type": "e1"}], "done": False}
        next_obs = {"economy": {"cash": 6000}, "units": [{"type": "1tnk"}], "done": False}

        value = fn(obs, 2, next_obs, False)
        assert isinstance(value, float)
        assert np.isfinite(value)

    def test_terminal_outcome_reward_is_positive_for_win(self):
        fn = RewardFunction()
        win_obs = {"result": "win", "economy": {"cash": 10000}, "units": [], "done": True}
        loss_obs = {"result": "lose", "economy": {"cash": 0}, "units": [], "done": True}

        assert fn(win_obs, 0, win_obs, True) > 0
        assert fn(loss_obs, 0, loss_obs, True) < 0


@pytest.mark.unit
class TestRecoveryWrapper:
    def test_wrapper_preserves_observation_and_step(self):
        class DummyEnv:
            def __init__(self):
                self.observation_space = None
                self.action_space = None
                self.closed = False

            def reset(self, *, seed=None, options=None):
                return np.array([1.0], dtype=np.float32), {"ok": True}

            def step(self, action):
                return np.array([2.0], dtype=np.float32), 0.5, False, False, {"action": action}

            def close(self):
                self.closed = True

        env = SupervisedEnv(DummyEnv())
        obs, info = env.reset()
        assert obs.shape == (1,)
        assert info["ok"] is True

        out = env.step(3)
        assert len(out) == 5
        assert out[1] == 0.5
        assert out[4]["action"] == 3
