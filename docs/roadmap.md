# Roadmap

## Phase 0 — Environment Validation（验证中，2026-05-18 更新）

**目标：** 双线验证 OpenRA-RL 和 ra2yrcpp 两条技术路线的可行性。

### 线路 A — OpenRA-RL 快速验证
- [x] 创建 Python 虚拟环境 (`<conda_env_path>`, Python 3.10.18)
- [ ] `pip install openra-rl` — **受阻**：权限错误导致安装失败
- [ ] 运行脚本 Bot 示例
- [ ] 评估观测空间/动作空间对 RL 训练的适配度
- [ ] 测试 headless 并行训练性能

### 线路 B — ra2yrcpp 重新验证
- [ ] 安装 CnCNet YR client package
- [ ] 使用 Syringe + yrpp-spawner 注入 ra2yrcpp
- [ ] 运行 pyra2yr 连通性测试
- [ ] 对比原方案 Blocker 是否已解除

**当前阻塞问题：**
1. **OpenRA-RL 安装失败**：`pip install openra-rl` 安装到最后阶段遇到权限错误（WinError 5），无法写入 `site-packages/openra_env`
2. **Git 不在系统 PATH**：无法执行 `git push` 同步到远程仓库

**Exit criteria：** 确定最终技术路线（OpenRA-RL 或 ra2yrcpp）。

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
