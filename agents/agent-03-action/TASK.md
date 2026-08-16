# Agent-03 · 动作空间

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-03 | **模块**：最小动作空间（高层离散动作 → OpenEnv 指令）
- **工作区**（独占写）：`agents/agent-03-action/`
- **名下主树文件**（独占写）：`ra2_env/action.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`

## 项目背景

Phase 1 动作空间是 10-16 个**高层离散动作**（`docs/architecture.md` §Action Space Phase 1）：建造电厂/矿场/兵营/重工、生产动员兵/坦克、全军进攻/防守基地/无操作。你要把离散动作 id 翻译成 OpenEnv 的 `CommandModel` 指令列表。OpenRA-RL 有 21 种 ActionType（move/attack/build/train/deploy/sell/place_building/set_stance/surrender…，见 `docs/roadmap.md` 线路 A 备注），但**每种动作的 CommandModel 字段组合语义未经实测**——你的首要工作是实证摸清。

必读：`scripts/a3_surrender_test.py`（DEPLOY/SURRENDER 已验证的调用范式）。

## 任务目标

1. **动作语义实证**（工作区 `probe_actions.py`）：server 起好后，逐个试ActionTypes 组合，验证哪些能真实改变游戏状态：
   - `BUILD`：造建筑需要哪些字段（target type？队列还是即时）？能否排队？
   - `TRAIN` / 生产：单位生产的指令形态？
   - `MOVE` / `ATTACK`：需要 actor_id + 目标坐标/目标 id？Phase 1 用「全军」语义如何批量下发？
   - `PLACE_BUILDING`：建筑落点如何给（坐标网格？自动选址）？——Phase 1 可先回避自由落点，用固定偏移或依赖 BUILD 自动放置（若引擎支持）
   把结论写进工作区 `ACTION_NOTES.md`（每条：指令构造 → 实测结果 → 证据 tick），这是全项目的核心知识资产。
2. **`DiscreteActionMapper`**（契约签名见章程 §5）：
   - `space()` → `Discrete(N)`，N ∈ [10, 16]，动作清单定义为模块级常量 `ACTIONS: list[str]`（id → 名称，如 `BUILD_POWER`/`TRAIN_CONSCRIPT`/`ATTACK_ALL`/`DEFEND_BASE`/`NOOP`…以实测可行的为准）。
   - `commands(action_id, obs)` → `list[CommandModel]`：**纯函数**，从 obs 读当前状态决定指令参数（如 ATTACK_ALL 要枚举己方战斗单位 actor_id）；不可执行时返回空列表（等同 NOOP），不抛异常。
   - `action_mask(obs)` → `np.ndarray[bool]` 或 `None`：屏蔽明显不可用动作（如没钱造不了建筑、没有兵则 ATTACK_ALL 无意义）。Phase 1 允许粗粒度，None=全可用也可接受，但实现了就是 Phase 3 的先行资产。
3. **单测**：mock obs 覆盖每个动作 id 的翻译正确性、非法 id 抛 `KeyError`/`IndexError`、mask 与 obs 状态一致性。放工作区 `tests/`，交 Agent-10 收编。

## 技术要点

- 指令构造照 a3 范式：`CommandModel(action=ActionType.X, actor_id=..., ...)`，其余字段以 `openra_env.models` 源码（venv A site-packages 里读）+ 实测为准。
- `commands()` 一次可返回多条 CommandModel（一 step 多指令），OpenEnv 的 `OpenRAAction(commands=[...])` 支持列表。
- 「全军进攻」类语义：无正式编队接口时，枚举己方单位逐个 MOVE/ATTACK 到敌方基地方向；具体可行方案以实测为准，写进 ACTION_NOTES.md。
- 不依赖 Agent-01/02：输入 obs 为 OpenEnv observation model，可独立开发（真实联调在他们集成后）。

## 接口契约（v1 冻结）

```python
class DiscreteActionMapper:
    def space(self) -> gymnasium.spaces.Discrete: ...
    def commands(self, action_id: int, obs) -> list[CommandModel]: ...
    def action_mask(self, obs) -> np.ndarray | None: ...
```

- **你依赖**：无代码依赖；参考 Agent-02 的 `obs_schema.md`（BOARD 上线后留意）。
- **被依赖**：Agent-01（RA2Env.step 调你的 `commands`）、Agent-06（随机采样需要你的动作清单与 mask）。

## 验收标准（DoD）

- [ ] `ACTION_NOTES.md` 覆盖全部 ACTIONS 清单中动作的实测证据
- [ ] `commands()` 纯函数、无 obs 副作用、空列表降级不抛异常
- [ ] mock 单测全绿
- [ ] 已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
