# CLAUDE.md

> AI 上下文入口，保持精简。详细内容见 `docs/`。

## Project

RA2_RL — 基于强化学习的《尤里的复仇》AI 训练框架。

## Current Status

**Phase 0 — Environment Validation ✅ 达成**（2026-06-11，线路 B 全线打通）

- **线路 B (ra2yrcpp 原版注入)**：✅ 完整跑通。补丁版 spawner `Ra2Game412-rl\gamemd-spawn-ra2yrcpp.exe -SPAWN` 启动游戏 → pyra2yr 连 `127.0.0.1:14521` 逐帧读状态 → deploy MCV 指令生效 → 一局完整 episode（开局→defeated→EXIT_GAME）。验证脚本在 `scripts/`（gen_spawn_b3 / b4_connect_test / b5_command_test）。
- **线路 A (OpenRA-RL)**：Docker Desktop 装在 `D:\DockerDesktop`（数据 `D:\DockerData`，不占 C 盘），doctor 全绿，server 容器 healthy（端口 8000），OpenEnv reset/step/观测/奖励验证通过；`done=True` 长跑验证中。注意：镜像 `latest` tag 只有 arm64，**必须拉 `0.4.1` 再本地 tag 成 latest**。
- **ADR-0005 已定稿（Accepted，2026-06-11）**：预案 3 双线并存——训练主路 OpenRA-RL headless，ra2yrcpp 作原版保真验证/录像旁路。

详见 [`docs/roadmap.md`](docs/roadmap.md)（含线路 B 踩坑记录）。

## Key Documents

- [`README.md`](README.md) — 项目概览
- [`docs/architecture.md`](docs/architecture.md) — 系统架构
- [`docs/roadmap.md`](docs/roadmap.md) — 开发路线图 + Phase 0 踩坑记录
- [`docs/technical-notes.md`](docs/technical-notes.md) — 技术约束
- [`docs/adr/`](docs/adr/) — 架构决策记录

## Multi-Agent Collaboration

Phase 1 起采用 10 Agent 并行开发：工作区 `agents/agent-XX-*/`（TASK.md 任务书 + PROGRESS.md 进度日志），协作章程 [`agents/README.md`](agents/README.md)（写权限边界、接口契约 v1、Git 纪律），共享看板 [`agents/BOARD.md`](agents/BOARD.md)（进度互见/广播/决策）。新会话或新 Agent **先读章程再开工**。

## Core Constraints

1. **测试/训练用 `Ra2Game412-rl\` 纯净副本**，不动原 `Ra2Game412\`（ADR-0004 放宽后的现行约束）
2. **`pyra2yr` 不提供 Gymnasium 接口**，需自行封装 `RA2Env`；其 `Game` 启动器在 Windows 上不可用（仅 Docker/Wine），需手动启动 spawner
3. **线路 B 跑训练必须开真实游戏窗口**（原版无 headless），并行度受限——这是 ADR-0005 权衡的核心
4. **每次开游戏窗口测试后必须清理 gamemd 进程**（用户要求：不留窗口）

## Stack

双轨：
- A: openra-rl 0.4.1 (OpenEnv) @ `E:\conda_envs\ra2rl`（Python 3.10）+ Docker `ghcr.io/yxc20089/openra-rl:0.4.1`
- B: ra2yrcpp `ee215f5` + pyra2yr 0.3.0 @ `E:\conda_envs\ra2rl-b`（Python 3.11）
- 下游：Gymnasium → Stable Baselines 3 (PPO) → PyTorch

## Next Step

1. Phase 1：`RA2Env` 最小 Gymnasium 环境 —— 10 Agent 并行开发（见 `agents/`，出口标准：随机 Agent 连续 100 局不崩溃）
2. 提交纪律：多 Agent 日常集成按 `agents/README.md` 章程自主 commit/push（conventional 格式 + 只报名下文件）；重大决策/契约变更仍需用户确认
