# 架构说明（中文）

## 项目定位

RA2_RL 是一个面向《红色警戒2：尤里的复仇》(YR) 的强化学习环境与训练框架。系统由三层组成：

1. 训练层：Gymnasium / Stable Baselines 3 / PPO
2. 环境抽象层：RA2Env、ObservationBuilder、ActionMapper、RewardFunction
3. 游戏运行时层：ra2yrcpp / pyra2yr / OpenRA-RL

其目标是把 RTS 游戏状态转换成标准 RL 训练接口，并在真实游戏环境中完成实验闭环。

## 总体架构

```text
      +---------------------------+
      | RL Agent / PPO / Policy   |
      +-------------+-------------+
                    |
                    v
      +---------------------------+
      | RA2Env (Gymnasium-style)  |
      | - reset()                 |
      | - step()                  |
      | - observation builder     |
      | - action mapper           |
      | - reward function         |
      +-------------+-------------+
                    |
                    v
      +---------------------------+
      | Game runtime adapter      |
      | - ra2yrcpp / pyra2yr      |
      | - OpenRA-RL bridge        |
      +-------------+-------------+
                    |
                    v
      +---------------------------+
      | Game process / engine     |
      | Yuri's Revenge / OpenRA   |
      +---------------------------+
```

## 关键组件

### 1. RA2Env

RA2Env 是整个项目对外的核心接口，负责：

- 初始化环境
- 读取状态
- 处理动作
- 计算奖励
- 判定终止条件
- 管理重置与回收

在 Phase 1 中，目标是实现一个最小可运行版本，保证随机 Agent 能稳定完成多个 episode。

### 2. ObservationBuilder

负责把底层游戏状态转换成模型可直接消费的观测向量或结构化数据，典型包括：

- 经济状态
- 资源状态
- 单位状态
- 建筑状态
- 空间地图特征
- 可见敌方信息

设计目标是兼顾：

- 可训练性
- 低延迟
- 封装稳定性

### 3. DiscreteActionMapper

将离散 RL 动作映射到真实游戏的命令：

- 移动
- 攻击
- 建造
- 训练单位
- 选择目标
- 放置建筑
- 其他基础 RTS 操作

这一层的关键任务是把大而复杂的 RTS 指令压缩到一个更小、更稳定的动作集合。

### 4. RewardFunction

用于把环境反馈转成可训练信号，通常包括：

- 胜负奖励
- 资源增长奖励
- 单位伤害与损失对比
- 建筑状态反馈
- 经济效率奖励

目标是让 RL Agent 既能获得目标导向反馈，又不会被过度稀疏奖励阻塞。

### 5. Recovery / Stability layer

真实 RTS 环境中经常出现：

- game window loss
- connection timeout
- engine crash
- action timeout
- invalid state read

因此需要超时保护、状态检查、自动恢复和 episode 兜底逻辑。这个模块用于提高训练稳定性。

## 双轨设计

### 轨道 A：OpenRA-RL

适合：

- 快速原型
- 无头环境训练
- 更简单的开发循环
- 对外开放式研究和演示

优点：

- 环境更容易控制
- Python 接口更成熟
- 更适合公开代码和团队协作

缺点：

- 不是原版 YR 稳定实现
- 需要接受重制引擎带来的泛化差异

### 轨道 B：ra2yrcpp + pyra2yr

适合：

- 真实保真验证
- 原版游戏运行时接入
- 战术与对局机制研究

优点：

- 最接近原版 YR
- 能直接读取真实游戏状态
- 更符合“真实战场训练”的目标

缺点：

- 需要处理原始游戏窗口、版本差异和注入问题
- 对环境要求更高，训练并行度较低

## 执行流程

```text
初始化环境
   ↓
启动游戏进程 / 连接 runtime
   ↓
读取 state
   ↓
ObservationBuilder 生成观测
   ↓
Agent 选择动作
   ↓
ActionMapper 转成游戏命令
   ↓
Game process 执行
   ↓
更新 state / reward / done
   ↓
继续下一 step
```

## 设计原则

1. 保留真实环境的结构复杂度，但要抽象出标准接口
2. 让环境对 RL 框架可用，而不是只为写脚本服务
3. 保证环境可复现和可调试
4. 分离训练和验证路径，避免互相污染
5. 保持 OpenRA 训练快、YR 保真真实这两条线并存

## 一致性约束

- 原版游戏测试只能使用纯净副本，不触碰原始目录
- 遇到真实窗口测试时需要清理 game process
- 不把训练环境中的游戏修补和工程部署混在一起
- 公开仓库应尽量保持结构、文档和运行说明一致

## 后续重点

当前项目的核心目标是：

- 完成最小 Gym 环境
- 让随机 Agent 连续跑多局不崩
- 建立训练基线
- 再提升到保真原版战斗控制和重构训练流程

这也是该项目最合理的工程顺序。
