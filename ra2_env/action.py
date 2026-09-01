from __future__ import annotations

from typing import Any

import numpy as np


class DiscreteActionMapper:
    """Minimal discrete action mapper for Phase 1.

    The action space is compact and fixed-size so that a local random-agent can
    be used for smoke tests before any more advanced action logic is added.
    """

    def __init__(self, n_actions: int = 10):
        self.n_actions = int(n_actions)

    def space(self):
        import gymnasium as gym

        return gym.spaces.Discrete(self.n_actions)

    def commands(self, action_id: int, obs: Any):
        action_map = {
            0: {"action": "noop"},
            1: {"action": "harvest"},
            2: {"action": "attack"},
            3: {"action": "build"},
            4: {"action": "defend"},
            5: {"action": "produce"},
            6: {"action": "move"},
            7: {"action": "queue"},
            8: {"action": "repair"},
            9: {"action": "surrender"},
        }
        if action_id < 0 or action_id >= self.n_actions:
            raise ValueError(f"Unsupported action id: {action_id}")
        return [action_map.get(action_id, {"action": "noop"})]

    def action_mask(self, obs: Any):
        return np.ones(self.n_actions, dtype=np.float32)
