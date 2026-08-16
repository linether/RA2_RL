# Agent-04 · 奖励函数

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-04 | **模块**：混合奖励函数（稀疏 + 稠密 + 课程表）
- **工作区**（独占写）：`agents/agent-04-reward/`
- **名下主树文件**（独占写）：`ra2_env/reward.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`（**纯 Python 模块，无需 server/Docker，完全离线可开发**）

## 项目背景

`docs/architecture.md` §Reward Function 定义了目标公式：

R = w_win·R_outcome + w_combat·R_combat + w_eco·R_eco

| 组件 | 类型 | 定义 |
|------|------|------|
| R_outcome | 稀疏 | 胜利 +1，失败 -1 |
| R_combat | 稠密 | 敌方受损价值 − 己方受损价值，按单位造价加权 |
| R_eco | 稠密 | 资源投入产出比，囤积未消费资金给负惩罚 |

**Curriculum**：初期高权重稠密奖励引导，后期逐步提升稀疏奖励权重。奖励设计是 RL 成败的最大杠杆之一，参考 `docs/lessons-from-macrogym.md` 的奖励塑造教训。

## 任务目标

实现 `ra2_env/reward.py`：

1. **`RewardWeights` dataclass**：`w_win / w_combat / w_eco: float`，默认值给依据（写注释引用 architecture.md）。
2. **`RewardFunction`**（契约签名见章程 §5）：
   - `__call__(obs, action_id, next_obs, done) -> float`：**纯函数语义**——只从相邻两帧 obs 差分计算，无内部累计状态（RA2Env 可能重开 episode，有状态的奖励会算错）。
   - `R_combat`：Δ(敌方总价值) − Δ(己方总价值)，单位价值 = 造价表 `COSTS`；「受损」含阵亡（列表消失）与掉血（若 obs 有 hp 字段，按 hp 比例折算价值）。
   - `R_eco`：现金流健康度——收入增长（cash Δ + 已花在建/造上的价值）、囤积惩罚（cash 超过阈值部分给负项，鼓励把钱变成战斗力）。
   - `R_outcome`：`done=True` 时按 `next_obs.result` 给 ±1（win/lose；draw 给 0）。
3. **造价表 `COSTS: dict[str, float]`**：RA2 单位/建筑造价（动员兵 100、犀牛坦克 900、电厂 600、矿场 2000、MCV 2000…以 OpenRA RA2 mod 数值为基准，查得到的写实测值，查不到的给合理估计并在注释标注 `# estimated`）。类型键与 Agent-02 的类型全集对齐——通过 BOARD 与 02 确认后冻结 v1，后续新增类型追加即可。
4. **课程表 `weight_schedule(progress: float) -> RewardWeights`**：`progress ∈ [0,1]`（训练进度），线性/分段插值从「稠密主导」过渡到「稀疏主导」；初始/终末权重写成模块常量并注释理由。
5. **数值纪律**：每步 reward 建议裁剪到 `[-10, 10]`（`np.clip`，防异常大值炸掉 PPO）；所有分量在 docstring 给公式与量级估计。
6. **单测**（放工作区 `tests/`，交 Agent-10 收编）：手工构造 obs 对覆盖——开局无变化（R≈0 仅 eco 项）、己方损兵、敌方损兵、大额囤积、胜/负终结、纯函数性（同输入两次调用同输出）。

## 技术要点

- 输入 obs 是 OpenEnv observation model（`obs.units/buildings/visible_enemies/economy.cash/result`，详见 a2 脚本）。用简单 dataclass mock 即可全离线开发。
- **可见性陷阱**：`visible_enemies` 受战争迷雾影响，敌人进出视野会造成 Δ 假跳变——设计上要处理（如按「可见敌军总价值变化」只负向计损、或对敌价值下降设置死亡置信阈值），你的处理方案写进 docstring 并在 BOARD 广播给 07（训练方要知道奖励的噪声特性）。
- OpenEnv 原生 `result.reward`（如 lose = -0.999）不要混用——那是引擎自带值，你的输出是唯一训练信号（Agent-01 已定：原生值进 `info`）。

## 接口契约（v1 冻结）

```python
class RewardFunction:
    def __call__(self, obs, action_id: int, next_obs, done: bool) -> float: ...
    def weights(self) -> RewardWeights: ...
def weight_schedule(progress: float) -> RewardWeights: ...
```

- **你依赖**：与 Agent-02 协调类型全集与造价表键名（BOARD 上对齐）；无代码依赖。
- **被依赖**：Agent-01（RA2Env 注入）、Agent-07（weight_schedule 用于训练中调权）。

## 验收标准（DoD）

- [ ] 公式、量级、裁剪、迷雾处理全部有 docstring 说明
- [ ] 纯函数性 + 边界单测全绿
- [ ] 造价表与 02 类型全集对齐并在 BOARD 登记
- [ ] 已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
