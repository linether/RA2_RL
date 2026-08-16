# Agent-01 · RA2Env 核心封装

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-01 | **模块**：RA2Env 核心（Gymnasium 环境主类）
- **工作区**（独占写）：`agents/agent-01-env-core/`
- **名下主树文件**（独占写）：`ra2_env/__init__.py`、`ra2_env/env.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`（Python 3.10，openra-rl 0.4.1）

## 项目背景

RA2_RL 用强化学习训练红警 2 AI。Phase 0 已双线打通（ADR-0005 Accepted）：训练主路为 OpenRA-RL（Docker headless，服务端 :8000，OpenEnv 异步接口）。当前为 **Phase 1：最小 Gymnasium 环境**。你的 `RA2Env` 是全系统枢纽——上游桥接 OpenEnv 异步客户端，下游供 SB3 PPO 与所有测试使用。

必读：`docs/architecture.md`（目标架构）、`docs/roadmap.md` Phase 1 条目、`scripts/a2_episode_test.py` 与 `scripts/a3_surrender_test.py`（OpenEnv 真实用法，照抄其调用模式）。

## 任务目标

实现 `ra2_env/env.py` 的 `RA2Env(gymnasium.Env)`：

1. **异步→同步桥接**：OpenEnv 是 `async with OpenRAEnv(base_url=...)` 的异步 API。用后台线程 + 专属 event loop（`asyncio.run_coroutine_threadsafe`）封装成同步 Gymnasium 接口；close 时干净关闭线程与 client。
2. **组件注入构造**：观测（Agent-02）、动作（Agent-03）、奖励（Agent-04）以构造参数注入，默认 `None` 时导入真实实现（契约签名见章程 §5）；`observation_space` / `action_space` 由组件 `.space()` 提供。
3. **生命周期**：`reset()` 返回 `(obs, info)`；`step(action_id)` 返回 `(obs, reward, terminated, truncated, info)`——`terminated` = 对局胜负（`result` 非 None），`truncated` = 达到 `max_episode_steps`；`close()` 幂等。注意 `reset()` 一次开局需 60-120 秒，超时要给足。
4. **错误面**：server 未启动 → 立即明确报错（提示先跑 `openra-rl server start`）；step 超时抛 `TimeoutError`。**恢复策略不归你**（归 Agent-05 的 `SupervisedEnv` 包装），你只负责把错误抛清楚。
5. **冒烟脚本**：工作区 `smoke_env.py`——server 在跑时 reset → 10×step → close 全程打印观测形状 / 奖励 / done。
6. **单测**：mock client（不用 Docker）覆盖构造、桥接线程启停、动作翻译调用、终止/截断语义，放工作区 `tests/`，交 Agent-10 收编。

## 技术要点

- OpenEnv 用法照抄 a2/a3：`result = await env.step(OpenRAAction(commands=[...]))`，读 `result.observation / .reward / .done`；`obs.units[i].actor_id / .type`、`obs.buildings`、`obs.visible_enemies`、`obs.economy.cash`、`obs.tick`、`obs.result`。
- 动作翻译：`step(action_id)` 内调 `self.action_mapper.commands(action_id, obs)` 得 `CommandModel` 列表，包进 `OpenRAAction`。21 种 ActionType 的语义归 Agent-03，你不要自己拼 CommandModel。
- 奖励：`self.reward_fn(obs, action_id, next_obs, done)`。注意 OpenEnv 自带 `result.reward`——用它还是用注入的 reward_fn 要在 docstring 写明设计决定（建议：注入组件优先，`info["openra_reward"]` 保留原生值）。
- 用 `gymnasium.utils.env_checker.check_env` 自检（合理豁免项在 PROGRESS.md 注明）。

## 接口契约（v1 冻结，变更走 BOARD 决策日志）

```python
class RA2Env(gymnasium.Env):
    def __init__(self, base_url: str = "http://localhost:8000",
                 observation_builder=None,   # ObservationBuilder (Agent-02)
                 action_mapper=None,         # DiscreteActionMapper (Agent-03)
                 reward_fn=None,             # RewardFunction (Agent-04)
                 max_episode_steps: int = 20000) -> None: ...
```

- **你依赖**：02 / 03 / 04（未就绪时用工作区 stub `ra2_env/_stubs.py`，同签名）。
- **被依赖**：05（`SupervisedEnv` 包装你，不改你的代码）、06（压力测试）、07（训练）、08（评估）。
- 集成 `ra2_env/__init__.py` 时从各组件模块 re-export，形成 `from ra2_env import RA2Env` 的统一入口（与 02/03/04/05 的文件分工协商走 BOARD）。

## 验收标准（DoD）

- [ ] server 在跑时，冒烟脚本 reset → 10×step → close 全绿
- [ ] mock 单测全部通过；`check_env` 无未解释失败
- [ ] 契约签名与章程 §5 一致
- [ ] 已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
