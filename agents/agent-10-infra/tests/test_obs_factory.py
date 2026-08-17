"""conftest obs mock 工厂的自检单测。

覆盖：默认值语义、str 简写展开、对象直传不篡改、典型 fixture 内容、
真实模型（openra_env.models）与 stub 的字段一致性。"""

from __future__ import annotations

import pytest

from conftest import REAL_MODELS

pytestmark = pytest.mark.unit


class TestMakeObservationDefaults:
    def test_empty_observation_is_blank_slate(self, empty_observation):
        assert empty_observation.tick == 0
        assert empty_observation.economy.cash == 10000
        assert empty_observation.economy.power_provided == 0
        assert empty_observation.economy.power_drained == 0
        assert empty_observation.units == []
        assert empty_observation.buildings == []
        assert empty_observation.visible_enemies == []
        assert empty_observation.visible_enemy_buildings == []
        assert empty_observation.result == ""
        assert empty_observation.done is False

    def test_economy_fields_are_wired(self, make_observation):
        obs = make_observation(cash=4242, power_provided=300, power_drained=170)
        assert obs.economy.cash == 4242
        assert obs.economy.power_provided == 300
        assert obs.economy.power_drained == 170


class TestStringShorthand:
    def test_unit_strings_expand_to_models(self, make_observation):
        obs = make_observation(units=["e1", "1tnk", "harv"])
        assert [u.type for u in obs.units] == ["e1", "1tnk", "harv"]
        assert all(u.hp_percent == 1.0 for u in obs.units)

    def test_actor_ids_unique_within_test(self, make_observation):
        obs = make_observation(
            units=["e1", "e1"], visible_enemies=["e1"], buildings=["powr"]
        )
        ids = [u.actor_id for u in obs.units] + [
            u.actor_id for u in obs.visible_enemies
        ] + [b.actor_id for b in obs.buildings]
        assert len(ids) == len(set(ids)), "同一次 make_observation 内 actor_id 不得重复"

    def test_building_strings_expand_to_models(self, make_observation):
        obs = make_observation(buildings=["fact", "powr"])
        assert [b.type for b in obs.buildings] == ["fact", "powr"]
        assert all(b.is_powered for b in obs.buildings)

    def test_make_unit_overrides(self, make_unit):
        unit = make_unit("1tnk", hp_percent=0.5, cell_x=12, cell_y=34)
        assert unit.type == "1tnk"
        assert unit.hp_percent == 0.5
        assert (unit.cell_x, unit.cell_y) == (12, 34)

    def test_make_building_overrides(self, make_building):
        b = make_building("weap", power_amount=-25, is_powered=False)
        assert b.type == "weap"
        assert b.power_amount == -25
        assert b.is_powered is False


class TestObjectPassthrough:
    def test_prebuilt_objects_pass_through_untouched(self, make_observation, make_unit):
        unit = make_unit("mcv")
        before = vars(unit) if not REAL_MODELS else unit.model_dump()
        obs = make_observation(units=[unit])
        assert obs.units[0] is unit, "对象直传必须原样入列，不做拷贝"
        after = vars(unit) if not REAL_MODELS else unit.model_dump()
        assert before == after, "工厂不得篡改调用方传入的对象"

    def test_mixed_strings_and_objects(self, make_observation, make_unit):
        unit = make_unit("harv")
        obs = make_observation(units=["e1", unit, "1tnk"])
        assert [u.type for u in obs.units] == ["e1", "harv", "1tnk"]
        assert obs.units[1] is unit


class TestScenarioFixtures:
    def test_sample_observation_is_a_real_game_state(self, sample_observation):
        types = {b.type for b in sample_observation.buildings}
        assert "fact" in types, "典型局必须含已部署主基地（MCV 部署标志可观测）"
        assert "powr" in types and "proc" in types
        assert [u.type for u in sample_observation.units].count("1tnk") == 2
        assert len(sample_observation.visible_enemies) == 3
        assert sample_observation.tick > 0
        assert sample_observation.economy.power_provided > sample_observation.economy.power_drained

    def test_outcome_fixtures(self, won_observation, lost_observation):
        assert won_observation.result == "win" and won_observation.done is True
        assert lost_observation.result == "lose" and lost_observation.done is True

    def test_map_size_wiring(self, make_observation):
        obs = make_observation(map_size=(128, 128))
        assert obs.map_info.width == 128
        assert obs.map_info.height == 128


class TestStubParity:
    """真实模型可用时，验证工厂产出真实类型且字段访问路径一致。"""

    @pytest.mark.skipif(REAL_MODELS, reason="当前就是真实模型分支")
    def test_stub_branch_declared(self):
        # CI 最小依赖下走 stub 分支；此测试只是让两个分支都显式可见
        assert REAL_MODELS is False

    @pytest.mark.skipif(not REAL_MODELS, reason="未安装 openra-rl（CI stub 分支）")
    def test_factory_produces_real_models(self, make_observation):
        from openra_env.models import OpenRAObservation, UnitInfoModel

        obs = make_observation(units=["e1"])
        assert isinstance(obs, OpenRAObservation)
        assert isinstance(obs.units[0], UnitInfoModel)
