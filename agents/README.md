# 多 Agent 并行开发协作章程

> 本目录是 10 个 Agent 的协作中枢。**任何 Agent 开始工作前必须通读本文。**
> 章程由主项目维护，Agent 无权修改；发现章程问题请在 BOARD.md 广播区提案。

## 1. 总览

- **主仓库**：本仓库（`origin = https://github.com/linether/RA2_RL.git`，分支 `main`），所有集成分发的唯一来源。
- **Agent 工作区**：`agents/agent-XX-<模块名>/`，每个 Agent 独占，内含 `TASK.md`（任务书）与 `PROGRESS.md`（进度日志）。
- **共享看板**：`agents/BOARD.md`，所有人可读；每个 Agent 只能写属于自己的部分（见 §3）。
- **隔离原则**：只写自己的工作区与名下主树文件，其余全库一律只读。进度通过 BOARD.md 互见，代码通过集成流程汇入主树。

## 2. 目录结构

```
agents/
├── README.md                       # 本章程
├── BOARD.md                        # 共享进度看板（广播/决策）
├── agent-01-env-core/              # RA2Env 核心封装
├── agent-02-observation/           # 观测空间
├── agent-03-action/                # 动作空间
├── agent-04-reward/                # 奖励函数
├── agent-05-recovery/              # 稳定性与崩溃恢复
├── agent-06-random-agent/          # 随机 Agent 压力测试
├── agent-07-training/              # SB3/PPO 训练集成
├── agent-08-evaluation/            # 评估体系
├── agent-09-track-b/               # 线路 B 原版保真旁路
└── agent-10-infra/                 # 测试/CI/工程基础设施
```

主树交付目录（所有权见各 TASK.md）：

```
ra2_env/    # Gymnasium 环境包（01 核心 / 02 观测 / 03 动作 / 04 奖励 / 05 恢复，按文件分属）
train/      # 训练脚本（07）
eval/       # 评估脚本（08）
scripts/    # 工具脚本（06；trackb/ 子目录归 09）
tests/      # 单元测试（10 收编各 Agent 工作区测试）
.github/    # CI（10）
```

## 3. 硬性规则（违反 = 集成被拒）

1. **写权限边界**：
   - 可写：`agents/agent-XX-*/**`（自己的工作区）+ TASK.md 中列明的**名下主树文件**。
   - BOARD.md 只允许三种写入：自己那行表格、广播区追加**署名**条目、决策日志追加提案。
   - **严禁**改动他人工作区、他人名下文件、`Ra2Game412/`（原版游戏目录）、`agents/README.md`。
2. **游戏进程清理**：任何开真实游戏窗口的测试（仅 Agent-09 场景）结束后必须清理 `gamemd*.exe` 进程，不留窗口、不留进程。
3. **测试只用 `Ra2Game412-rl/` 纯净副本**，永不触碰 `Ra2Game412/` 原目录（ADR-0004 放宽后的现行约束）。
4. **Git 纪律**：
   - commit message 用 conventional 格式（`feat:` / `fix:` / `test:` / `docs:` / `chore:`），一次提交只做一件事。
   - push 前先 `git pull --rebase origin main`；遇到 `index.lock`（其他 Agent 正在操作 git）等待 5-10 秒重试。
   - **禁止** `git push --force`、禁止提交大型二进制/游戏文件（.gitignore 已拦截，勿绕过）。
   - 集成提交只触碰自己名下文件；rebase 冲突只可能发生在共享文件（BOARD.md）——冲突时保留双方内容再继续。
5. **接口契约冻结**：§5 契约 v1 已冻结。需要变更：先在 BOARD.md 决策日志提案 → 受影响 Agent 在广播区回复确认 → 提案方才能改签名并在 PROGRESS.md 记录版本号。
6. **不越界救火**：发现他人模块的 bug，在 BOARD.md 广播区报告，不要直接改别人代码。

## 4. 标准工作流

1. **启动**：读 `agents/README.md`（本文）→ 读自己 `TASK.md` → 读自己 `PROGRESS.md` 历史 → 浏览 `BOARD.md` 了解全局状态。
2. **开发**：一切代码先在工作区开发。工作区内按主树镜像路径放置，例如 `agents/agent-02-observation/ra2_env/observation.py`，便于集成时整体复制。
3. **自测**：模块单测 / 冒烟脚本放在工作区（如 `agents/agent-XX-*/tests/`），全部通过后才可集成。
4. **集成**：复制名下文件到主树路径 → 在主树跑相关测试 → `git add <名下文件>` → commit → `git pull --rebase origin main` → push。
5. **汇报**：每次会话结束或里程碑达成，更新：
   - 自己 `PROGRESS.md`（日志追加 + 状态/里程碑字段）；
   - `BOARD.md` 自己那行（状态、一句话进度、更新时间）。
6. **协作**：跨模块问题一律走 BOARD.md 广播区（署名追加），不得写入他人文件。

## 5. 接口契约（v1，2026-08-16 冻结）

> 签名以本节为准。开发期依赖方未就绪时，用同签名 stub 先行，集成时切换真实实现。

```python
# ra2_env/observation.py —— Agent-02
class ObservationBuilder:
    def space(self) -> "gymnasium.spaces.Box": ...      # float32 扁平向量，shape 固定
    def build(self, obs) -> "np.ndarray": ...           # obs = OpenEnv observation model

# ra2_env/action.py —— Agent-03
class DiscreteActionMapper:
    def space(self) -> "gymnasium.spaces.Discrete": ... # N ∈ [10, 16]
    def commands(self, action_id: int, obs) -> "list[CommandModel]": ...
    def action_mask(self, obs) -> "np.ndarray | None": ...  # None = 全部可用

# ra2_env/reward.py —— Agent-04
class RewardFunction:
    def __call__(self, obs, action_id: int, next_obs, done: bool) -> float: ...
    def weights(self) -> "RewardWeights": ...           # dataclass，支持课程表更新

# ra2_env/recovery.py —— Agent-05
class SupervisedEnv(gymnasium.Env): ...                 # 组合包装 inner_env，不修改被包装类
def ensure_server(base_url: str = "http://localhost:8000", timeout: float = 180.0) -> bool: ...

# ra2_env/env.py —— Agent-01
class RA2Env(gymnasium.Env):
    def __init__(self, base_url: str = "http://localhost:8000",
                 observation_builder=None, action_mapper=None, reward_fn=None,
                 max_episode_steps: int = 20000) -> None: ...

# eval/metrics.py —— Agent-08（Agent-07 的 eval 回调按此调用）
def evaluate(policy, env, n_episodes: int, seed: int = 0) -> "dict": ...
```

**依赖关系图**：

```
02 观测 ┐
03 动作 ├─→ 01 RA2Env ──→ 06 压力测试 ──→ Phase 1 验收(连续100局不崩)
04 奖励 ┘        ↑
05 恢复(SupervisedEnv 包装 RA2Env) ─→ 06
01 RA2Env ─→ 07 训练 ─→ 08 评估        （07/08 期初可用 mock env 并行开发）
09 线路B ── 独立支线（与 01-08 仅通过 BOARD 协调，venv B）
10 基建 ── 横向支撑（收编单测 / CI / 依赖清单），不阻塞任何人
```

**启动顺序建议**：02、03、04、05、09、10 可立即开工（互不依赖）；01 用 stub 开工；06、07、08 先用 mock env 搭骨架，待 01 集成后切换真实环境。

## 6. Python 环境矩阵

| 线路 | venv | Python | 用途 | 关键包 |
|------|------|--------|------|--------|
| A（训练主路） | `E:\conda_envs\ra2rl\Scripts\python.exe` | 3.10.18 | Agent 01-08、10 | openra-rl 0.4.1、numpy 2.2.6 |
| B（原版保真） | `E:\conda_envs\ra2rl-b\Scripts\python.exe` | 3.11.15 | Agent-09 专属 | pyra2yr 0.3.0、numpy 1.26.4 |

- 两 venv 的 Python/numpy 版本不兼容，**不可混装**；新依赖装进对应 venv 后，把包名+版本报告到 BOARD.md 广播区，由 Agent-10 收编进 requirements。
- 线路 A 服务端：`openra-rl server start`（Docker，:8000）。**镜像坑**：上游 `latest` 只有 arm64，必须拉 `0.4.1` 再本地 tag 成 latest（本机已完成）。
- 线路 B：手动启动 `Ra2Game412-rl\gamemd-spawn-ra2yrcpp.exe -SPAWN`，端口 14521；窗口化需 16 位色深；详见 `docs/roadmap.md` 线路 B 踩坑记录。

## 7. 状态图例

| 图标 | 含义 |
|------|------|
| 🟡 | 待启动 |
| 🔵 | 进行中 |
| 🟢 | 可集成（自测通过，等待/已完成集成） |
| ✅ | 完成（DoD 全达成） |
| 🔴 | 阻塞（详见 PROGRESS.md 与广播区） |
