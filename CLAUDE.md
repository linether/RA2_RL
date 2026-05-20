# CLAUDE.md

> AI 上下文入口，保持精简。详细内容见 `docs/`。

## Project

RA2_RL — 基于强化学习的《尤里的复仇》AI 训练框架。

## Current Status

**Phase 0 — Environment Validation**（进行中,2026-05-21)

双线验证中:
- **线路 A (OpenRA-RL)**:`openra-rl 0.4.1` 已装,import 通过。**当前 Blocker:Docker Desktop 未安装**(`openra-rl doctor` 报 `Docker CLI: not found`)
- **线路 B (ra2yrcpp)**:未启动。调研报告显示 2026-01 起 ra2yrcpp 已适配 CnCNet YR client,原"必须纯净版 1.001"的 Blocker 可能已解除

详见 [`docs/roadmap.md`](docs/roadmap.md) 与 [`docs/research-report-2026-05.md`](docs/research-report-2026-05.md)。

## Key Documents

- [`README.md`](README.md) — 项目概览
- [`docs/architecture.md`](docs/architecture.md) — 系统架构
- [`docs/roadmap.md`](docs/roadmap.md) — 开发路线图
- [`docs/technical-notes.md`](docs/technical-notes.md) — 技术约束
- [`docs/adr/`](docs/adr/) — 架构决策记录

## Core Constraints

1. **开发环境必须是纯净版 YR 1.001**（含 Ares/Phobos 的目录不能用，见 ADR-0004）
2. **`pyra2yr` 不提供 Gymnasium 接口**，需自行封装 `RA2Env`
3. **Phase 0 未通过前不写 RL 代码**

## Stack

`pyra2yr` + `ra2yrcpp` → Gymnasium → Stable Baselines 3 (PPO) → PyTorch

## Next Step

1. **线路 A**:安装 Docker Desktop → `openra-rl doctor` 全绿 → 跑脚本 Bot 示例
2. **线路 B**(并行):获取 CnCNet YR client + ra2yrcpp Release → Syringe 注入 → pyra2yr 连通性
3. 任一线通过即可 Exit Phase 0,写 ADR-0005 决定最终技术栈
