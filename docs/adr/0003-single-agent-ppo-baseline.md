# ADR-0003: 使用单 Agent PPO 作为基线架构

## Status

Accepted

## Context

RTS 游戏 AI 的前沿研究（AlphaStar、SMAC 等）普遍采用复杂架构：分层 RL、多智能体 CTDE (Centralized Training Decentralized Execution)、League Training 等。这些方法在大型团队 + 充足算力下能取得 SOTA 表现，但对单人开发者不现实：

- AlphaStar 级别的 League Training 依赖大规模并行采样与专用基础设施
- 多智能体 CTDE (如 MAPPO、QMIX) 实现复杂，调试成本高
- 分层 RL 的 Macro/Micro 拆分在缺乏稳定基线时难以验证有效性

项目当前状态是**尚无任何可运行的环境**。在环境稳定性、训练管线、奖励设计都未验证的情况下引入复杂架构，会将故障定位难度显著放大。

## Decision

初期采用 **单 Agent + PPO** 作为基线：

- 使用 Stable Baselines 3 的 PPO 实现（成熟、文档完善、调试友好）
- 单一策略网络处理所有决策（不分层）
- 目标：在固定地图上击败原版 Easy AI

分层、多智能体、自我博弈等高级方法延后到 Phase 5，且仅在单 Agent 基线稳定后引入。

## Consequences

**收益：**
- 最小化早期复杂度，便于快速验证环境与训练管线
- PPO 对超参数相对鲁棒，适合作为基线
- Stable Baselines 3 降低实现错误风险

**代价：**
- 单 Agent 架构的策略上限有限，难以处理大规模单位微操
- 无法直接复现 AlphaStar 级别的表现

**升级路径：**
- Phase 5 可在稳定基线上叠加脚本化 Macro + 学习 Micro 的分层
- 若数据充足，可尝试自我博弈（当前策略 vs 历史 checkpoint），无需 League 基础设施
