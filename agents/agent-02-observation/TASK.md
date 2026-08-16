# Agent-02 · 观测空间

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-02 | **模块**：最小观测空间（扁平向量）
- **工作区**（独占写）：`agents/agent-02-observation/`
- **名下主树文件**（独占写）：`ra2_env/observation.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`

## 项目背景

Phase 1 需要最小可训练观测：把 OpenEnv 的结构化 observation（经济 / 单位列表 / 建筑列表 / 可见敌军）压缩为**固定长度 float32 扁平向量**（`docs/architecture.md` §Observation Space Phase 1）。你的输出直接喂给 PPO，布局稳定性是训练的前提——**向量每一维都必须在 docstring 中登记**。

参考：`scripts/a2_episode_test.py`（observation 字段真实用法）、`docs/lessons-from-macrogym.md`（观测设计经验）。

## 任务目标

实现 `ra2_env/observation.py`：

1. **字段探查**：先写工作区 `probe_obs.py` 连 server（`openra-rl server start` 后跑 a2 的循环）dump 一局 observation 的完整 schema（字段名 / 类型 / 取值范围 / units 条目的全部属性），存 `agents/agent-02-observation/obs_schema.md`。这是你设计布局的依据，也是给 Agent-03/04 的参考资料（通过 BOARD 告知存在）。
2. **`ObservationBuilder`**（契约签名见章程 §5）：
   - `space()` → `gymnasium.spaces.Box`，float32，固定 shape，合理 bounds（计数类用 `[0, max]`，经济类 `[0, inf]`，比例类 `[0, 1]`）。
   - `build(obs)` → `np.ndarray`，**纯函数语义**（不修改入参、无隐藏状态、确定性）。
3. **布局设计**（Phase 1 最小集，参照 architecture.md）：
   - 经济：cash、电力供给/需求（schema 里有什么用什么，缺失的在 obs_schema.md 注明）
   - 计数：己方单位按类型聚合、己方建筑按类型聚合、可见敌军按类型聚合（类型全集固定列表，见第 4 条）
   - 标志：MCV 是否已部署（有无 fact）、对局 `result` 编码
   - 每个分段在模块 docstring 中用表格登记：`[起止下标 | 含义 | 归一化方式]`
4. **类型全集**：RA2 关键类型固定列表（建筑：powerplant/refinery/barracks/factory/…；单位：mcv/miner/rhino/… 以 probe 实测的 `type` 字符串为准），映射到固定下标，未知类型归入 `other` 桶并计数。全集列表定义为模块级常量，改动走 BOARD。
5. **数值健康**：cash 等大数值必须归一化（如 `log1p` 或 `/1e4`），避免 PPO 输入爆炸；在 docstring 写明每个分段的归一化公式。
6. **单测**：手工构造 mock obs（按你的 obs_schema.md）覆盖：空局（无单位）、满局、未知类型入 other 桶、确定性（同输入同输出）。放工作区 `tests/`，交 Agent-10 收编。

## 技术要点

- `obs.units` / `obs.buildings` / `obs.visible_enemies` 是列表，元素含 `actor_id`、`type`（实测为准）——probe 先行，不要凭猜测写字段。
- 不依赖 Agent-01：`build()` 的输入就是 OpenEnv 的 observation model，可独立开发；用 pydantic/dataclass mock 即可单测。
- `np.float32` 全程，`build()` 输出 shape 必须与 `space()` 严格一致（写一个断言单测）。

## 接口契约（v1 冻结）

```python
class ObservationBuilder:
    def space(self) -> gymnasium.spaces.Box: ...
    def build(self, obs) -> np.ndarray: ...
```

- **你依赖**：无（完全独立，可立即开工）。
- **被依赖**：Agent-01（RA2Env 构造注入）、Agent-04（可能读你的布局文档设计经济奖励项）。

## 验收标准（DoD）

- [ ] `obs_schema.md` 完整记录真实 observation 结构
- [ ] 布局表齐全、归一化公式明确、`space()` 与 `build()` shape 断言通过
- [ ] mock 单测全绿（含边界：空局/未知类型/确定性）
- [ ] 已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
