# Agent 协作看板

> 规则（见 `agents/README.md` §3）：每个 Agent 只能写 **自己那行表格**、**广播区追加署名条目**、**决策日志追加提案**。
> 看板冲突（rebase）时保留双方内容。

## 进度总览

| # | 模块 | 工作区 | 状态 | 一句话进度 | 更新时间 |
|---|------|--------|------|------------|----------|
| 01 | RA2Env 核心封装 | `agents/agent-01-env-core` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 02 | 观测空间 | `agents/agent-02-observation` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 03 | 动作空间 | `agents/agent-03-action` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 04 | 奖励函数 | `agents/agent-04-reward` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 05 | 稳定性与崩溃恢复 | `agents/agent-05-recovery` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 06 | 随机 Agent 压力测试 | `agents/agent-06-random-agent` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 07 | SB3/PPO 训练集成 | `agents/agent-07-training` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 08 | 评估体系 | `agents/agent-08-evaluation` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 09 | 线路 B 原版保真旁路 | `agents/agent-09-track-b` | 🟡 | 任务书已下发，等待启动 | 2026-08-16 |
| 10 | 测试/CI/工程基础设施 | `agents/agent-10-infra` | 🔵 | M1 测试基建已集成：pyproject markers + conftest obs 工厂 + 13 单测全绿；下一步 CI | 2026-08-16 |

## 主树集成登记

> 集成名下文件到主树后在此追加一行：`| 日期 | Agent | 文件 | commit |`。未登记的集成视为未完成。

| 日期 | Agent | 文件 | commit |
|------|-------|------|--------|
| 2026-08-16 | 10 | `pyproject.toml`、`tests/conftest.py`、`tests/test_obs_factory.py` | (本提交) |

## 广播区（追加式，必须署名）

> 用途：跨模块提问、bug 报告、依赖版本通报、契约变更回复。格式：`[Agent-XX · 日期] 内容`。

- [Agent-10 · 2026-08-16] **依赖通报（章程 §6）**：venv A 新装 `pytest 9.1.1`、`ruff 0.16.3`（测试/lint 工具，将进 requirements-track-a 的 dev 组）。其余 venv A 包无变化。
- [Agent-10 · 2026-08-16] **测试基建上线（M1），全队请注意跑法**：主树 `pytest` 默认只跑 `unit` marker（`addopts=-m unit`）；跑其他组用 `-m` 覆盖（如 `pytest -m "unit or integration"`）；`integration`/`trackb` 需设 `RA2RL_INTEGRATION=1`/`RA2RL_TRACKB=1` 才会执行，否则 skip（防 CI/裸跑误开游戏）。**造 obs 请用 `tests/conftest.py` 的工厂**（`make_observation`/`make_unit`/`make_building` + `empty/sample/won/lost_observation` 场景 fixture），勿在各测试手写模型类；工厂在无 openra-rl 的环境自动回退 stub，单测不必装重依赖。另：`scripts/*` 已豁免 ruff E501（b4_connect_test.py:40 有 115 字符遗留长行，风格问题不拦 CI，语义检查仍保留；如需清理请名下 Agent 自理）。

## 决策日志（追加式提案）

> 契约/章程变更流程：提案 → 受影响方在广播区回复确认 → 提案方实施并在此记录结果。

- [2026-08-16 · 主项目] 章程与接口契约 v1 冻结，10 工作区初始化完成，Phase 1 并行开发启动。
