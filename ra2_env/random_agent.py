from __future__ import annotations

import random
from typing import Any

import numpy as np


class RandomPolicy:
    """Simple policy for local smoke tests and pressure validation."""

    def __init__(self, action_space: Any, seed: int | None = None):
        self.action_space = action_space
        self.rng = random.Random(seed)

    def sample_action(self) -> int:
        if hasattr(self.action_space, "n"):
            return self.rng.randrange(int(self.action_space.n))
        if hasattr(self.action_space, "sample"):
            return int(self.action_space.sample())
        raise ValueError("Action space does not expose a valid sample interface.")


def run_random_agent(
    env: Any,
    episodes: int = 10,
    max_steps: int = 20,
    seed: int | None = None,
) -> dict[str, Any]:
    """Run a simple random-policy loop and return summary metrics."""
    policy = RandomPolicy(env.action_space, seed=seed)
    rewards = []
    completed = 0
    crashes = 0

    for episode in range(episodes):
        try:
            obs, info = env.reset(seed=seed if seed is not None else episode)
            episode_reward = 0.0
            for _ in range(max_steps):
                action = policy.sample_action()
                obs, reward, terminated, truncated, info = env.step(action)
                episode_reward += float(reward)
                if terminated or truncated:
                    break
            rewards.append(episode_reward)
            completed += 1
        except Exception:
            crashes += 1
            continue
    return {
        "episodes": episodes,
        "completed": completed,
        "crashes": crashes,
        "avg_reward": float(np.mean(rewards)) if rewards else 0.0,
        "total_reward": float(np.sum(rewards)),
        "max_steps": max_steps,
    }
