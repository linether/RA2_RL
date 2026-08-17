"""RA2_RL 共享测试夹具：OpenEnv observation mock 工厂（v0）。

全队单测造 obs 一律走本文件的 ``make_observation`` / ``make_unit`` /
``make_building`` 工厂，不要在各测试文件里手写模型类——布局变更时只改这里。

字段依据（Agent-02 的 ``obs_schema.md`` 公布后对齐升 v1）：
- ``scripts/a2_episode_test.py`` 一局实测用法：tick / economy.cash / units /
  buildings / visible_enemies / result；
- ``openra_env.models``（openra-rl 0.4.1）的字段名与默认值。

依赖策略：优先用真实 ``openra_env.models``（venv A 已装 openra-rl）；未安装时
回退到本文件内字段名一致、默认值相同的 dataclass stub，保证 CI 只装最小依赖
（pytest + numpy + gymnasium）也能跑全部 unit 测试。

marker 兜底：integration / trackb 测试默认 skip（CI 无 Docker/游戏），
设 ``RA2RL_INTEGRATION=1`` / ``RA2RL_TRACKB=1`` 显式启用。
"""

from __future__ import annotations

import itertools
import os
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import pytest

try:  # 真实模型优先（venv A / 本地装了 openra-rl 时生效）
    from openra_env.models import (
        BuildingInfoModel,
        EconomyInfo,
        MapInfoModel,
        MilitaryInfo,
        OpenRAObservation,
        ProductionInfoModel,
        UnitInfoModel,
    )

    REAL_MODELS = True
except ImportError:  # 最小依赖兜底：字段名/默认值与 openra_env.models 对齐
    REAL_MODELS = False

    @dataclass
    class EconomyInfo:
        cash: int = 0
        power_provided: int = 0
        power_drained: int = 0

    @dataclass
    class MilitaryInfo:
        units_killed: int = 0
        units_lost: int = 0
        buildings_killed: int = 0
        buildings_lost: int = 0
        active_unit_count: int = 0
        kills_cost: int = 0
        deaths_cost: int = 0
        assets_value: int = 0

    @dataclass
    class UnitInfoModel:
        actor_id: int
        type: str
        pos_x: int = 0
        pos_y: int = 0
        cell_x: int = 0
        cell_y: int = 0
        hp_percent: float = 1.0
        owner: str = ""
        attack_range: int = 0
        is_building: bool = False

    @dataclass
    class BuildingInfoModel:
        actor_id: int
        type: str
        pos_x: int = 0
        pos_y: int = 0
        hp_percent: float = 1.0
        owner: str = ""
        is_powered: bool = True
        rally_x: int = -1
        rally_y: int = -1
        power_amount: int = 0
        cell_x: int = 0
        cell_y: int = 0

    @dataclass
    class ProductionInfoModel:
        queue_type: str
        item: str
        remaining_ticks: int = 0

    @dataclass
    class MapInfoModel:
        width: int = 0
        height: int = 0
        map_name: str = ""

    @dataclass
    class OpenRAObservation:
        # Observation 基类字段（openenv.core.env_server.types）
        done: bool = False
        reward: Any = None
        metadata: Dict[str, Any] = field(default_factory=dict)
        # OpenRAObservation 自有字段
        tick: int = 0
        economy: EconomyInfo = field(default_factory=EconomyInfo)
        military: MilitaryInfo = field(default_factory=MilitaryInfo)
        units: List[UnitInfoModel] = field(default_factory=list)
        buildings: List[BuildingInfoModel] = field(default_factory=list)
        production: List[ProductionInfoModel] = field(default_factory=list)
        visible_enemies: List[UnitInfoModel] = field(default_factory=list)
        visible_enemy_buildings: List[BuildingInfoModel] = field(default_factory=list)
        map_info: MapInfoModel = field(default_factory=MapInfoModel)
        available_production: List[str] = field(default_factory=list)
        result: str = ""
        spatial_map: str = ""
        spatial_channels: int = 0
        reward_vector: Optional[Dict[str, float]] = None


def pytest_runtest_setup(item: pytest.Item) -> None:
    """marker 兜底：integration/trackb 在未显式启用时 skip，防止 CI / 裸跑误开游戏。"""
    if "integration" in item.keywords and os.environ.get("RA2RL_INTEGRATION") != "1":
        pytest.skip("integration 测试需 openra-rl Docker server；设 RA2RL_INTEGRATION=1 启用")
    if "trackb" in item.keywords and os.environ.get("RA2RL_TRACKB") != "1":
        pytest.skip("trackb 测试需真实游戏进程（venv B）；设 RA2RL_TRACKB=1 启用")


def _expand(items: Any, make: Any) -> list:
    """列表元素支持 str 简写：'e1' 自动展开为默认字段的该类型对象。"""
    return [make(x) if isinstance(x, str) else x for x in items]


@pytest.fixture
def _actor_ids():
    # 单位与建筑共享同一 ID 空间（真实游戏 actor_id 全局唯一）
    return itertools.count(1)


@pytest.fixture
def make_unit(_actor_ids):
    """UnitInfo 工厂：接受 type 字符串 + 任意字段覆盖；actor_id 测试内自动唯一。"""

    def _make(type: str = "e1", **overrides: Any) -> UnitInfoModel:
        values: Dict[str, Any] = {
            "actor_id": next(_actor_ids),
            "type": type,
            "pos_x": 0,
            "pos_y": 0,
            "cell_x": 0,
            "cell_y": 0,
            "hp_percent": 1.0,
            "owner": "",
            "attack_range": 0,
            "is_building": False,
        }
        values.update(overrides)
        return UnitInfoModel(**values)

    return _make


@pytest.fixture
def make_building(_actor_ids):
    """BuildingInfo 工厂：接受 type 字符串 + 任意字段覆盖；actor_id 测试内自动唯一。"""

    def _make(type: str = "powr", **overrides: Any) -> BuildingInfoModel:
        values: Dict[str, Any] = {
            "actor_id": next(_actor_ids),
            "type": type,
            "pos_x": 0,
            "pos_y": 0,
            "hp_percent": 1.0,
            "owner": "",
            "is_powered": True,
            "rally_x": -1,
            "rally_y": -1,
            "power_amount": 0,
            "cell_x": 0,
            "cell_y": 0,
        }
        values.update(overrides)
        return BuildingInfoModel(**values)

    return _make


@pytest.fixture
def make_observation(make_unit, make_building):
    """OpenRAObservation 工厂：经济/敌我列表用关键字注入，条目支持 str 简写。

    例::

        obs = make_observation(
            cash=3000, power_provided=300, power_drained=150,
            buildings=["fact", "powr", "powr"],
            units=["e1", "1tnk"],
            visible_enemies=["e1"],
            result="win", done=True,
        )
    """

    def _make(
        *,
        tick: int = 0,
        cash: int = 10000,
        power_provided: int = 0,
        power_drained: int = 0,
        units: Any = (),
        buildings: Any = (),
        visible_enemies: Any = (),
        visible_enemy_buildings: Any = (),
        production: Any = (),
        available_production: Any = (),
        map_size: Any = None,
        military: Any = None,
        result: str = "",
        done: bool = False,
        **overrides: Any,
    ) -> OpenRAObservation:
        values: Dict[str, Any] = {
            "tick": tick,
            "economy": EconomyInfo(
                cash=cash, power_provided=power_provided, power_drained=power_drained
            ),
            "military": military if military is not None else MilitaryInfo(),
            "units": _expand(units, make_unit),
            "buildings": _expand(buildings, make_building),
            "production": list(production),
            "visible_enemies": _expand(visible_enemies, make_unit),
            "visible_enemy_buildings": _expand(visible_enemy_buildings, make_building),
            "available_production": list(available_production),
            "map_info": (
                MapInfoModel(width=map_size[0], height=map_size[1])
                if map_size is not None
                else MapInfoModel()
            ),
            "result": result,
            "done": done,
        }
        values.update(overrides)
        return OpenRAObservation(**values)

    return _make


@pytest.fixture
def empty_observation(make_observation):
    """空局（刚 reset）：tick=0、开局资金、无任何单位/建筑/敌情。"""
    return make_observation()


@pytest.fixture
def sample_observation(make_observation):
    """典型中期局面：基地成体系（fact 已部署）、有部队、有可见敌军、经济运转中。"""
    return make_observation(
        tick=5000,
        cash=3000,
        power_provided=300,
        power_drained=150,
        buildings=["fact", "powr", "powr", "proc", "barr", "weap"],
        units=["e1", "e1", "e1", "1tnk", "1tnk", "harv", "harv"],
        visible_enemies=["e1", "e1", "1tnk"],
        available_production=["e1", "1tnk", "harv"],
    )


@pytest.fixture
def won_observation(make_observation):
    """胜局终局帧：result='win'、done=True。"""
    return make_observation(result="win", done=True)


@pytest.fixture
def lost_observation(make_observation):
    """败局终局帧：result='lose'、done=True。"""
    return make_observation(result="lose", done=True)
