from __future__ import annotations

from typing import Any


class RewardFunction:
    """Minimal reward function for local smoke tests.

    This intentionally keeps the reward computation simple and explainable.
    """

    def __call__(self, obs: Any, action_id: int, next_obs: Any, done: bool) -> float:
        economy = (obs or {}).get("economy", {}) if isinstance(obs, dict) else {}
        next_economy = (next_obs or {}).get("economy", {}) if isinstance(next_obs, dict) else {}
        cash_gain = float(next_economy.get("cash", 0.0)) - float(economy.get("cash", 0.0))

        result = (obs or {}).get("result", "") if isinstance(obs, dict) else ""
        next_result = (next_obs or {}).get("result", "") if isinstance(next_obs, dict) else ""

        reward = 0.01 * cash_gain

        if done and next_result == "win":
            reward += 1.0
        elif done and next_result == "lose":
            reward -= 1.0

        if done and result == "win" and next_result == "win":
            reward += 0.1

        return float(reward)
