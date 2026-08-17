# Agent-10 · 测试/CI/工程基础设施 — 进度日志

- **状态**：🔵 进行中
- **更新时间**：2026-08-16
- **当前里程碑**：M1 达成——pyproject + pytest markers + conftest fixture 工厂已集成主树

## 日志（新条目加在最上面）

### 2026-08-16 · M1：测试基建上线（已集成）
- **venv A 新增依赖**（已在 BOARD 通报）：pytest 9.1.1、ruff 0.16.3。
- **pyproject.toml**（主树根）：
  - pytest：markers `unit`/`integration`/`trackb` 三级；`addopts = "-m unit -ra"` 默认只跑 unit（CLI `-m` 可覆盖，如 `pytest -m "unit or integration"`）；`pythonpath = ["."]` 让 tests/ 可 import ra2_env/train/eval；`testpaths = ["tests"]`。
  - ruff：E/F 默认规则集，line-length 100，排除 `Ra2Game412*/`、`third_party/`、`debug_shots/`、`agents/`；`scripts/*` 豁免 E501（Phase 0 遗留脚本 b4_connect_test.py:40 有 115 字符打印行，属风格问题，已在 BOARD 说明——语义检查保留）。
  - 最小 `[project]` 元数据 + `[project.optional-dependencies].dev`（pytest/ruff/gymnasium/numpy），CI 将用 `pip install -e ".[dev]"`；运行依赖仍走 requirements/（待 M2 拆分）。
- **tests/conftest.py**（obs mock 工厂 v0）：
  - 字段依据 `scripts/a2_episode_test.py` 实测 + `openra_env.models`（openra-rl 0.4.1）定义；Agent-02 的 obs_schema.md 公布后对齐升 v1。
  - 工厂：`make_unit` / `make_building`（str 简写 + 字段覆盖）、`make_observation`（经济/敌我列表/胜负终局）；场景 fixture：`empty_observation`（开局）、`sample_observation`（中期：fact 已部署、三军齐备、有敌情）、`won_observation` / `lost_observation`。
  - 单位与建筑**共享 actor_id 计数器**（真实游戏 ID 全局唯一；自检单测抓出过两计数器撞号 bug）。
  - 依赖策略：真实 `openra_env.models` 优先，ImportError 回退字段名一致的同默认值 dataclass stub → CI 只装最小依赖也能跑 unit（已用 `sys.modules` 阻断法验证两分支均 13 passed）。
  - marker 兜底 hook：integration/trackb 未设 `RA2RL_INTEGRATION=1` / `RA2RL_TRACKB=1` 时 skip（已验证：默认 2 skipped，设变量后放行）。
- **tests/test_obs_factory.py**：13 个自检单测（默认值/str 展开/ID 唯一/对象直传不篡改/场景内容/stub 与真实模型双分支）。
- **自测**：工作区与主树均 `13 passed, 1 skipped in <0.1s`（skip 为分支声明测试，按环境二选一）；`ruff check .` 全绿。
- **集成**：pyproject.toml、tests/conftest.py、tests/test_obs_factory.py → 主树，BOARD 集成表已登记。

### 2026-08-16 · 初始化
- 任务书（TASK.md）下发，工作区就绪，等待启动。第一步：pyproject + pytest markers + conftest fixture 工厂。

## 下一步（M2 候选）

1. `.github/workflows/ci.yml`：windows-latest + Python 3.10，`pip install -e ".[dev]"` → `pytest`（即 `-m unit`）+ `ruff check .`；上线后在 BOARD 广播红灯规则。
2. `requirements/` 两轨拆分（等 BOARD 各 Agent 版本通报，先起草骨架）。
3. 根 `requirements.txt` 改指向（需 BOARD 提案一次）。
4. README 徽章提案（CI 上线后）。

## 阻塞 / 依赖

- 无阻塞；requirements 版本冻结依赖各 Agent 在 BOARD 的依赖通报。

## 给其他 Agent 的广播

- 已发：venv A 依赖通报（pytest/ruff）、测试基建用法通报（见 BOARD 广播区 2026-08-16 两条）。
