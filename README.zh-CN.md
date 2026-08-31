# RA2_RL

![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-Phase%200-orange.svg)
![Project](https://img.shields.io/badge/project-public-blueviolet.svg)

English: [README.md](README.md)

一个面向《红色警戒2：尤里的复仇》的强化学习环境与训练研究项目。

本仓库旨在为原始游戏运行时与 Gymnasium 风格接口之间建立清晰桥接，并提供用于训练和验证的入口，覆盖原版游戏路线和 OpenRA 相关实验路线。

## 这个项目存在的意义

目前多数 RTS 强化学习项目大多存在以下问题：

- 依赖自定义环境或模拟器，而不是原版游戏运行时
- 只关注 Agent 逻辑，而没有稳定可复用的训练环境
- 只停留在一次性原型阶段，缺少标准化环境抽象

本项目尝试做一件更困难但更有意义的事：让原版游戏成为真正可训练的 RL 环境，同时保留清晰稳定的接口设计。

## 当前状态

截至 2026-09-01，项目已进入较强的环境验证阶段：

- 原版游戏路线的 Phase 0 环境验证已被认为完成
- 项目已经验证了双轨策略：
  - 轨道 A：OpenRA-RL 作为主训练路线
  - 轨道 B：ra2yrcpp / pyra2yr 作为原版游戏保真验证路线
- 目前主要里程碑是 Phase 1：最小 Gymnasium 环境与随机 Agent 压力测试

详细进度见 [docs/roadmap.md](docs/roadmap.md) 与 [CLAUDE.md](CLAUDE.md)。

## 系统架构

```text
RL Training Stack
    ↓
RA2Env (Gymnasium-style interface)
    ↓
State / Action / Reward adapters
    ↓
Original-game bridge (ra2yrcpp / pyra2yr)
    ↓
Yuri's Revenge game process
```

本仓库采用双轨策略：

- 轨道 A：OpenRA-RL，用于无头/高效实验迭代
- 轨道 B：ra2yrcpp，用于原版保真度验证和回放检查

## 相关生态

本项目位于更大的 RTS AI / 研究工具链中：

- [OpenRA-RL](https://github.com/yxc20089/OpenRA-RL) — 一个围绕 OpenRA 构建 Python 环境和 Agent 栈的项目
- [ra2yrcpp](https://github.com/shmocz/ra2yrcpp) — 尤里复仇游戏进程的底层桥接
- [pyra2yr](https://github.com/shmocz/pyra2yr) — ra2yrcpp 的 Python 客户端层
- [Stable Baselines 3](https://stable-baselines3.readthedocs.io/) — RL 训练后端

与这些项目相比，本仓库定位为“桥接层”：提供原版游戏访问能力、标准化 RL 接口与可复现训练工作流。

## 项目结构

```text
RA2_RL/
├── README.md
├── README.zh-CN.md
├── CLAUDE.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── pyproject.toml
├── requirements/
├── requirements.txt
├── src/
│   └── ra2_rl/
│       └── env/
├── configs/
│   ├── README.md
│   └── runtime/
├── examples/
│   └── README.md
├── scripts/
├── tests/
├── train/
│   ├── README.md
│   ├── __init__.py
│   ├── train_ppo.py
│   └── configs/
│       ├── README.md
│       └── baseline.json
├── eval/
│   └── README.md
├── ra2_env/
├── docs/
│   ├── architecture.md
│   ├── architecture.zh-CN.md
│   ├── roadmap.md
│   ├── roadmap.zh-CN.md
│   ├── technical-notes.md
│   ├── technical-notes.zh-CN.md
│   └── adr/
├── agents/
│   ├── README.md
│   ├── BOARD.md
│   └── agent-*/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   └── workflows/
└── .gitignore
```

## 快速开始

### 依赖条件

- Python 3.10+
- 用于原版游戏验证路径的 Windows 10/11
- 轨道 B 测试所需的干净《尤里复仇》安装
- 轨道 A 开发所需的 OpenRA-RL 环境

### 安装

```bash
pip install -r requirements.txt
```

关于技术约束和环境配置，见：

- [docs/technical-notes.md](docs/technical-notes.md)
- [docs/roadmap.md](docs/roadmap.md)
- [docs/architecture.md](docs/architecture.md)

## 路线图

### Phase 0 — 环境验证

- 验证原版游戏和 OpenRA 两条路线
- 确认状态访问与命令控制是否可行
- 确立架构与约束条件

### Phase 1 — 最小 Gym 环境

- 实现 RA2Env：reset / step / close
- 标准化观测空间与动作空间
- 用随机策略进行压力测试

### Phase 2 — 基线训练

- 添加 PPO 基线与训练配置
- 保持评估方法可复现且可比较

### Phase 3+ — 增强与扩展

- 观测/动作空间增强
- 奖励塑形与训练稳健性
- 基础设施与部署优化

## 文档

- [docs/architecture.md](docs/architecture.md) — 架构与系统分解
- [docs/architecture.zh-CN.md](docs/architecture.zh-CN.md) — 中文架构说明
- [docs/roadmap.md](docs/roadmap.md) — 当前路线图与里程碑
- [docs/roadmap.zh-CN.md](docs/roadmap.zh-CN.md) — 中文路线图
- [docs/technical-notes.md](docs/technical-notes.md) — 约束、注意事项和环境说明
- [docs/technical-notes.zh-CN.md](docs/technical-notes.zh-CN.md) — 中文技术说明
- [docs/adr/](docs/adr/) — 架构决策记录
- [agents/README.md](agents/README.md) — 多 Agent 协作规范

## 参与贡献

欢迎任何形式的贡献，尤其是：

- RL 环境设计
- 观测/动作空间改进
- 奖励工程
- 稳定性与恢复机制
- 评估与 benchmark
- 项目文档与可复现性

请参考 [CONTRIBUTING.md](CONTRIBUTING.md) 获取开发流程、提交规范和代码贡献说明。

## 安全

如果发现安全问题或敏感漏洞，请不要在公开 issue 中直接披露，参考 [SECURITY.md](SECURITY.md)。

## 许可证

本项目基于 MIT License 开源，详情见 [LICENSE](LICENSE)。

## 致谢

- Red Alert 2: Yuri's Revenge
- ra2yrcpp and pyra2yr
- OpenRA-RL
- Gymnasium and Stable Baselines 3
