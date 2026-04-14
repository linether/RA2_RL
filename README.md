# RA2_RL

基于深度强化学习的《红色警戒2：尤里的复仇》AI 训练框架。

通过内存注入获取游戏状态，封装为 Gymnasium 标准环境，使用 Stable Baselines 3 进行 PPO 训练。

## Features

- **低延迟状态接口** — 通过 `ra2yrcpp` 注入游戏进程，< 5ms 读取结构化状态
- **Gymnasium 兼容** — 标准 `reset()` / `step()` 接口，可直接接入主流 RL 框架
- **多模态观测** — 标量统计 / 空间特征图 / 实体列表
- **混合奖励** — 稀疏胜负奖励 + 稠密战斗/经济 shaping

## Architecture

```
Training (SB3 / PPO)
    ↕
RA2Env (Gymnasium)
    ↕  Socket + Protobuf
ra2yrcpp (C++ DLL, injected)
    ↕
gamemd.exe (Yuri's Revenge 1.001)
```

详见 [`docs/architecture.md`](docs/architecture.md)。

## Status

Phase 0 — Environment Validation（进行中）

路线图见 [`docs/roadmap.md`](docs/roadmap.md)。

## Requirements

- Windows 10/11
- Python 3.10+
- Yuri's Revenge 1.001（纯净版，不含 Ares/Phobos 等社区补丁）
- [`ra2yrcpp`](https://github.com/shmocz/ra2yrcpp) 预编译 DLL

## Installation

```bash
pip install -r requirements.txt
```

游戏与 DLL 配置详见 [`docs/technical-notes.md`](docs/technical-notes.md)。

## Documentation

- [Architecture](docs/architecture.md) — 系统设计与模块划分
- [Roadmap](docs/roadmap.md) — 开发路线图
- [Technical Notes](docs/technical-notes.md) — 技术约束与已知限制
- [ADR](docs/adr/) — 架构决策记录

## Acknowledgements

- [`shmocz/ra2yrcpp`](https://github.com/shmocz/ra2yrcpp) — C++ game interface
- [`shmocz/pyra2yr`](https://github.com/shmocz/pyra2yr) — Python client
- [Stable Baselines 3](https://stable-baselines3.readthedocs.io/)

## License

MIT
