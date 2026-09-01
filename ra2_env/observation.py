from __future__ import annotations

from typing import Any, Mapping

import numpy as np


class ObservationBuilder:
    """Minimal phase-1 observation builder.

    Produces a fixed-size numeric vector summarizing basic state for local
    Gymnasium tests and future real-environment integration.
    """

    def space(self):
        import gymnasium as gym

        return gym.spaces.Box(low=-1e6, high=1e6, shape=(10,), dtype=np.float32)

    def build(self, obs: Mapping[str, Any] | Any) -> np.ndarray:
        economy = obs.get("economy", {}) if isinstance(obs, dict) else {}
        cash = float(economy.get("cash", 0.0))
        power_provided = float(economy.get("power_provided", 0.0))
        power_drained = float(economy.get("power_drained", 0.0))

        units = obs.get("units", []) if isinstance(obs, dict) else []
        buildings = obs.get("buildings", []) if isinstance(obs, dict) else []
        enemies = obs.get("visible_enemies", []) if isinstance(obs, dict) else []
        enemy_buildings = obs.get("visible_enemy_buildings", []) if isinstance(obs, dict) else []
        tick = float(obs.get("tick", 0)) if isinstance(obs, dict) else 0.0

        vector = np.array(
            [
                cash,
                power_provided,
                power_drained,
                float(len(units)),
                float(len(buildings)),
                float(len(enemies)),
                float(len(enemy_buildings)),
                tick,
                1.0 if obs.get("done", False) else 0.0,
                1.0 if obs.get("result", "") == "win" else 0.0,
            ],
            dtype=np.float32,
        )
        return vector
