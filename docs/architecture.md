# Architecture

## Overview

RA2_RL 是一个针对《红色警戒2：尤里的复仇》(YR) 的强化学习环境与训练框架。系统由三层组成：

```
┌─────────────────────────────────────────────┐
│          Training Layer (Python)            │
│   Stable Baselines 3 / PPO / TensorBoard    │
└─────────────────────────────────────────────┘
                      ↕
┌─────────────────────────────────────────────┐
│       Environment Layer (Python)            │
│   Gymnasium-compatible RA2Env               │
│   (observation / action / reward)           │
└─────────────────────────────────────────────┘
                      ↕  Socket + Protobuf
┌─────────────────────────────────────────────┐
│       Game Interface Layer (C++ DLL)        │
│   ra2yrcpp (injected via Syringe)           │
│   Hooks into gamemd.exe via YRpp            │
└─────────────────────────────────────────────┘
                      ↕
┌─────────────────────────────────────────────┐
│    Yuri's Revenge 1.001 (gamemd.exe)        │
└─────────────────────────────────────────────┘
```

## Components

### Game Interface Layer

**ra2yrcpp** — C++ DLL，通过 Syringe 注入 `gamemd.exe`。利用 YRpp 访问游戏内部类，Hook 游戏主循环实现 lock-step 同步，将状态序列化为 Protocol Buffers 经 Socket 发送。

**pyra2yr** — Python 客户端，封装 Socket 通信与 Protobuf 解码，提供异步状态查询与指令执行接口。

### Environment Layer

实现 `gymnasium.Env` 标准接口的 `RA2Env`，封装 pyra2yr 的异步 API，包含：

- **Observation** — 多模态观测（标量统计、空间特征图、实体列表）
- **Action** — 离散动作空间 + Action Masking
- **Reward** — 混合稀疏/稠密奖励
- **Episode management** — 启动、重置、崩溃恢复

### Training Layer

使用 Stable Baselines 3 的 PPO 算法，TensorBoard 记录训练指标。单 Agent 架构作为基线，后期可扩展至分层或自我博弈。

## Observation Space

### Phase 1 (Minimal)

扁平向量（`gymnasium.spaces.Box`）：
- 资金、电力供给、电力需求、当前帧
- 按单位类型聚合的己方/敌方数量
- 按建筑类型聚合的己方数量
- 科技状态标志位

### Phase 3 (Extended)

- **Spatial features:** 128×128 多通道网格（地形、己方单位、敌方单位、建筑、战争迷雾）
- **Entity list:** 变长单位列表，支持 Transformer 自注意力

## Action Space

### Phase 1 (Minimal)

`gymnasium.spaces.Discrete(N)`，约 10-15 个高层动作：

| 类别 | 动作 |
|------|------|
| 建造 | 电厂 / 矿场 / 兵营 / 重工 |
| 生产 | 动员兵 / 坦克 |
| 指令 | 全军进攻 / 防守基地 / 无操作 |

### Phase 3 (Extended)

- 建筑放置坐标
- 编队选择与控制
- Action Masking（屏蔽不可用动作）

## Reward Function

$$R = w_{win} \cdot R_{outcome} + w_{combat} \cdot R_{combat} + w_{eco} \cdot R_{eco}$$

| 组件 | 类型 | 描述 |
|------|------|------|
| $R_{outcome}$ | 稀疏 | 胜利 +1，失败 -1 |
| $R_{combat}$ | 稠密 | 敌方受损价值 − 己方受损价值，按单位造价加权 |
| $R_{eco}$ | 稠密 | 资源投入产出比，囤积未消费资金给予负向惩罚 |

**Curriculum：** 初期高权重稠密奖励，后期逐步提升稀疏奖励权重。

## Directory Layout

```
RA2_RL/
├── README.md
├── CLAUDE.md
├── LICENSE
├── .gitignore
├── requirements.txt
├── docs/
│   ├── architecture.md          # 本文档
│   ├── roadmap.md               # 开发路线图
│   ├── technical-notes.md       # 技术说明与约束
│   └── adr/                     # Architecture Decision Records
│       ├── README.md
│       ├── 0001-target-yuris-revenge.md
│       ├── 0002-memory-injection.md
│       ├── 0003-single-agent-ppo-baseline.md
│       └── 0004-clean-yr-as-dev-env.md
├── ra2_env/                     # Gymnasium 环境封装
│   ├── __init__.py
│   ├── env.py
│   ├── observation.py
│   ├── action.py
│   └── reward.py
├── train/                       # 训练脚本
│   ├── train_ppo.py
│   └── config.py
├── eval/                        # 评估脚本
│   └── evaluate.py
├── scripts/                     # 工具脚本
│   ├── test_pyra2yr.py
│   ├── test_env.py
│   └── random_agent.py
└── tests/                       # 单元测试
```
