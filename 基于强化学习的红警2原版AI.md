# 基于强化学习的红色警戒 2 原版 AI

## 项目概述

本项目旨在用强化学习（RL）训练一个能玩红色警戒 2 原版的 AI。通过 `pyra2yr` + `ra2yrcpp` 进行内存注入获取游戏状态，封装为 Gymnasium 标准环境，使用 Stable Baselines 3 (PPO) 进行训练。

**目标游戏：** 红色警戒 2 原版（`game.exe`），如 ra2yrcpp 不兼容则退回尤里的复仇（`gamemd.exe`，RA2 超集）。

---

## 技术路线：内存注入

### 方案对比

| 维度 | 屏幕监控 (OpenCV/CNN) | 内存读取 (DLL Injection/Protobuf) |
|------|----------------------|----------------------------------|
| 延迟 | 高 (50-100ms) | 极低 (< 5ms) |
| 可观测性 | 仅屏幕可见区域 | 全图数据，属性精确 |
| 计算开销 | 极高（CNN 处理图像） | 极低（结构化数据） |
| 稳定性 | 受分辨率、UI 缩放影响 | 内存基址不变则极稳定 |

**选择内存读取**，与 AlphaStar 读取 StarCraft II API 的思路一致。

### 核心依赖：pyra2yr + ra2yrcpp

- **ra2yrcpp** (C++ DLL)：通过 Syringe 注入游戏进程，利用 YRpp 访问游戏内部类，将状态序列化为 Protocol Buffers 格式，支持同步步进（Lock-step）
- **pyra2yr** (Python)：封装与 DLL 的 Socket 通信，提供 Python 端接口

> **注意：** pyra2yr 不提供现成的 Gymnasium 环境，需自行封装 `RA2Env(gymnasium.Env)`。

### RA2 原版 vs 尤里的复仇

| 维度 | RA2 原版 | 尤里的复仇 (YR) |
|------|----------|-----------------|
| 可执行文件 | `game.exe` | `gamemd.exe` |
| ra2yrcpp 支持 | 需验证（hook 地址可能不同） | 官方目标 |
| 社区工具链 | 较少 | Ares/Phobos 生态完善 |

ra2yrcpp 基于 YRpp（Yuri's Revenge++ Library），主要针对 `gamemd.exe`。Phase 0 需验证对 `game.exe` 的兼容性，不兼容则使用 YR。

---

## 技术栈

| 组件 | 选型 | 理由 |
|------|------|------|
| 游戏接口 | pyra2yr + ra2yrcpp | 唯一可用的 RA2 结构化接口 |
| 环境标准 | Gymnasium | 业界标准 |
| RL 框架 | Stable Baselines 3 | 文档好、PPO 开箱即用 |
| 深度学习 | PyTorch | SB3 底层依赖 |
| 日志 | TensorBoard | SB3 原生支持 |
| 序列化 | Protocol Buffers | ra2yrcpp 原生格式 |

---

## 环境设计

### 观测空间（初版：扁平向量）

**全局统计 (Scalar Features):**
- 当前资金、电力供给、电力需求、当前时间帧
- 各类型单位数量（己方/敌方可见）
- 各类型建筑数量
- 科技等级状态

后续扩展：
- 空间特征图 (128x128 网格：地形、己方单位、敌方单位、建筑、战争迷雾)
- 实体列表 (变长列表 + Transformer 自注意力处理)

### 动作空间（初版：离散空间，10-15 个动作）

- 建造：电厂 / 矿场 / 兵营 / 重工
- 生产：动员兵 / 坦克
- 指令：全军进攻 / 防守基地 / 无操作

后续扩展：
- 建筑放置坐标
- 编队控制
- Action Masking（屏蔽不可执行动作）

### 奖励函数

$$R_{total} = w_{win} \cdot R_{outcome} + w_{combat} \cdot R_{combat} + w_{eco} \cdot R_{eco}$$

| 组件 | 类型 | 描述 |
|------|------|------|
| $R_{outcome}$ | 稀疏 | 胜利 +1, 失败 -1 |
| $R_{combat}$ | 稠密 | 敌方受损价值 - 己方受损价值（按单位造价加权） |
| $R_{eco}$ | 稠密 | 资源采集效率，囤积不消费给予惩罚 |

训练策略：初期仅用稠密奖励（学会采矿、造兵、打架），后期逐步增加稀疏奖励权重（学会为胜利牺牲短期利益）。

---

## RL 架构

### 初版：单 Agent PPO

使用 Stable Baselines 3 的 PPO 算法，单一策略网络处理所有决策。目标：击败 Easy AI。

### 后续扩展：分层架构

仅在初版稳定后考虑：

**宏观代理 (Macro-Agent)：**
- 职责：经济运营、科技攀升、兵力生产
- 时间尺度：每 5-10 秒决策一次
- 动作：Build / Train / AttackOrder

**微观代理 (Micro-Agent)：**
- 职责：单位移动、攻击、技能释放
- 时间尺度：每 1-3 帧决策一次
- 参考 SMAC 的 MAPPO/QMIX，权重共享

---

## 项目结构

```
RA2_RL/
├── ra2_env/
│   ├── __init__.py
│   ├── env.py          # RA2Env(gymnasium.Env) 核心
│   ├── observation.py  # 观测空间定义
│   ├── action.py       # 动作空间定义
│   └── reward.py       # 奖励函数
├── train/
│   ├── train_ppo.py    # PPO 训练脚本
│   └── config.py       # 超参数配置
├── eval/
│   └── evaluate.py     # 评估脚本
├── scripts/
│   ├── test_env.py     # 环境测试脚本
│   └── random_agent.py # 随机 agent 验证
├── requirements.txt
└── README.md
```

---

## 开发路线图

### Phase 0: 验证冲刺 (1-2 周)

**目标：证明 pyra2yr + ra2yrcpp 可用**

1. 安装 RA2 原版
2. 验证 ra2yrcpp 对 `game.exe` 的兼容性（不兼容则用 YR）
3. 构建/安装 ra2yrcpp，通过 Syringe 注入 DLL
4. 安装 pyra2yr，运行示例验证状态读取和指令执行
5. 记录所有问题

**退出标准：** 能程序化启动游戏、读取状态、发送指令。

### Phase 1: 最小 Gymnasium 环境 (3-4 周)

**目标：random agent 能跑完整局不崩溃**

- 实现 `RA2Env`：`reset()` 启动新对局，`step()` 执行动作并返回观测
- 最小观测空间（扁平向量）+ 最小动作空间（离散）
- 简单奖励函数
- 崩溃自动重启

### Phase 2: 首个 RL Agent (2-3 周)

**目标：PPO 击败 Easy AI**

- SB3 + PPO 训练
- 固定场景：1v1, 简单地图, Easy AI
- TensorBoard 日志监控
- 迭代奖励 shaping

### Phase 3: 环境增强 (4-6 周)

- 空间特征图 + 实体列表
- 扩展动作空间 + Action Masking
- 提升对手难度

### Phase 4: 基础设施加固 (可选)

- Docker + Wine 容器化
- 并行环境 (SubprocVecEnv)
- 崩溃恢复

### Phase 5: 高级架构 (可选)

- 分层 Agent（脚本宏观 + 学习微操）
- Transformer 实体处理
- 自我博弈（当前 vs 历史 checkpoint）

---

## 风险与缓解

| 风险 | 概率 | 缓解策略 |
|------|------|----------|
| ra2yrcpp 不兼容 RA2 原版 | 中高 | 退回 YR 开发 |
| pyra2yr/ra2yrcpp 不稳定 | 中高 | Phase 0 快速验证；备选：OpenRA-RL |
| RA2 频繁崩溃 | 高 | 环境层 try-catch + 自动重启 |
| 训练速度慢（单实例） | 高 | 先接受，Phase 4 再并行化 |
| 动作/观测空间设计不当 | 中 | 最小起步，根据训练结果迭代 |
| shmocz 停止维护 | 中 | 尽早 fork，理解核心代码 |

---

## 关键外部资源

- [shmocz/pyra2yr](https://github.com/shmocz/pyra2yr) — Python RA2 接口
- [shmocz/ra2yrcpp](https://github.com/shmocz/ra2yrcpp) — C++ DLL 后端
- [yxc20089/OpenRA-RL](https://github.com/yxc20089/OpenRA-RL) — 备选方案（RA1 Gymnasium 环境）
- [Stable Baselines 3](https://stable-baselines3.readthedocs.io/) — RL 训练框架
