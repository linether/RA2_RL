"""RA2_RL environment API.

This package exposes the minimal Gymnasium-compatible contract used by the
project for Phase 1 local validation and future integration with the real
OpenRA/OpenEnv runtime and original-game bridge.
"""

from .action import DiscreteActionMapper
from .env import RA2Env
from .observation import ObservationBuilder
from .openra_adapter import OpenRAAdapter
from .recovery import SupervisedEnv
from .reward import RewardFunction
from .runtime_adapter import RuntimeClientBridge

__all__ = [
    "RA2Env",
    "ObservationBuilder",
    "DiscreteActionMapper",
    "RewardFunction",
    "SupervisedEnv",
    "RuntimeClientBridge",
    "OpenRAAdapter",
]
