# CLAUDE.md

> AI 上下文入口，保持精简。详细内容见 `docs/`。

## Project

RA2_RL — 基于强化学习的《尤里的复仇》AI 训练框架。

## Current Status

**Phase 0 — Environment Validation**（进行中）

Blocker: 需要纯净版 YR 1.001（无 Ares/Phobos 补丁），平台版 `Ra2Game412/` 不可用于 `ra2yrcpp` 注入。

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

1. 获取纯净版 YR 1.001 → `Ra2Clean/`
2. 下载 `ra2yrcpp` 预编译 DLL
3. `pip install pyra2yr` 并运行连通性测试
