# Roadmap

## Phase 0 — Environment Validation

**目标：** 验证 `pyra2yr` + `ra2yrcpp` 能稳定读取游戏状态并发送指令。

- [ ] 获取纯净版 YR 1.001 安装
- [ ] 从 `shmocz/ra2yrcpp` Releases 下载预编译 DLL
- [ ] 通过 Syringe 注入 DLL 到 `gamemd.exe`
- [ ] `pip install pyra2yr`
- [ ] 运行连通性测试：启动游戏 → 读取状态 → 发送指令

**Exit criteria:** 能程序化启动游戏、读取状态、执行建造与移动指令。

## Phase 1 — Minimal Gym Environment

**目标：** 可运行的 Gymnasium 环境，支持随机 Agent 完整跑完一局。

- [ ] 实现 `RA2Env` 核心类（`reset` / `step` / `close`）
- [ ] 实现最小观测空间（扁平向量）
- [ ] 实现最小动作空间（10-15 个离散动作）
- [ ] 实现基础奖励函数
- [ ] 崩溃恢复与自动重启
- [ ] 随机 Agent 压力测试

**Exit criteria:** 随机 Agent 连续跑 100 局不崩溃。

## Phase 2 — Baseline Agent

**目标：** PPO 基线击败原版 Easy AI。

- [ ] Stable Baselines 3 集成
- [ ] 训练配置与超参数
- [ ] TensorBoard 监控
- [ ] 奖励 shaping 迭代
- [ ] 评估脚本

**Exit criteria:** PPO Agent vs Easy AI 胜率 > 50%（固定地图）。

## Phase 3 — Observation & Action Enrichment

**目标：** 支持更复杂的策略学习。

- [ ] 添加空间特征图（minimap grid）
- [ ] 添加实体列表与 Transformer encoder
- [ ] 扩展动作空间（建筑放置、编队控制）
- [ ] Action Masking
- [ ] 更高难度对手

**Exit criteria:** Agent 展现出超越 Tank Rush 的策略多样性。

## Phase 4 — Infrastructure Hardening

**目标：** 支持规模化训练。

- [ ] Docker 容器化（考虑 Wine headless 或 Windows Server）
- [ ] 并行环境（SubprocVecEnv 或 Ray）
- [ ] Checkpoint 管理与断点续训
- [ ] 崩溃自动恢复增强

## Phase 5 — Advanced Architecture

**目标：** 探索高级 RL 技术。

- [ ] 分层 Agent（Macro + Micro）
- [ ] 自我博弈（current vs historical checkpoints）
- [ ] 部署适配（训练环境 → 对战平台）
