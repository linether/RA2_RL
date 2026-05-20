# 来自 RA-MacroGym 的设计经验与规划

> 把 CA6126 作业(RA-MacroGym v2.2)做完之后,沉淀给 RA2_RL 用的设计经验与阶段规划。
> 这些不是"假设",是在一个我们自己设计 + 自己训了出来的 1v1 简化版红警 RL 环境里直接得到的反馈。

## 1. 上下文:RA-MacroGym 是什么

- 1v1 抽象红警宏观环境(无空间网格,纯资源/兵力维度)
- 29 维 obs / 15 离散动作
- 三阶段战斗:遭遇 → 包围 → 反包围;Lanchester 平方律 + ±15% 噪声 + 防守 +2 加成
- 战争迷雾(POMDP):scout 快照 + 接触刷新 + 0.25/step 主动侦察概率
- 训了 DQN baseline / PPO / dawn-PPO-v2(对手池训练)
- 循环赛冠军 dawn-PPO-v2 总胜率 97%,对 nina-PPO 双向横扫 20/20

这一切在一个**几小时就能跑完一次完整训练**的玩具环境里完成。RA2_RL 的训练成本会高几个数量级,
所以 MacroGym 验证过的设计决策值得直接采纳,**踩过的坑不要在 RA2 上重踩**。

## 2. 验证过的设计决策(可直接迁移)

### 2.1 PPO + VecNormalize + SB3 是够用的起点

- 不要一上来上 IMPALA / SAC / 自研 RL。SB3 PPO 在 1v1 简化场景能跑出 97% 胜率,Phase 1 用 PPO 没问题。
- **VecNormalize 必加**。MacroGym 早期不加,reward 量级失衡,训练直接发散。
- ADR-0003 选 PPO baseline 是对的,**保留**。

### 2.2 离散动作空间足够开局

- 15 个动作就能描述 1v1 红警宏观。
- RA2 真实动作空间大得多(单位组 + 位置 + 命令),但 **Phase 1 还是按 roadmap 的 10–15 个离散动作开局**,
  不要急着上结构化/分层动作。
- MacroGym 里某些动作组合永远没用(如"什么都不造"),靠 reward 自然剔除比 action mask 简单。
  RA2 建议先用 reward 引导,再上 mask。

### 2.3 Reward shaping 是 RL 项目唯一真正的"难"

MacroGym 的 reward 演化(踩坑顺序):

| 版本 | 配方 | 现象 |
|---|---|---|
| v1 | +1 赢 / -1 输 | 稀疏到死,学不出来 |
| v2 | + 经济密集 reward | 出现"光攒钱不打"病理 |
| v3 | + 兵力差密集 reward | 学会造兵但被规则 baseline 反推 |
| v4 | + 反包围 bonus | 解决"全压上 → 老家被偷"陷阱 |
| v5(终版) | 上 + 终局 ±1 主导,中间 reward 量级 ±0.1 | 收敛快、稳 |

给 RA2_RL 的建议:
- 从 Phase 2 第一天起把 reward shaping 当**主线工作**,别期望默认"摧毁对手 +N"能直接学出来
- 中间 reward 控制在 ±0.1 量级,终局 ±1 主导
- dense reward 上之前先确认它指向的子目标是赢的必要条件,否则奖励错的行为

### 2.4 对手池训练是"能赢 → 主宰"的关键

dawn-PPO-v2 用对手池(rule-aggressive / balanced / economic / dqn-baseline / nina-PPO)训练,
67% → 97%,直接横扫之前的冠军。

对 RA2_RL:
- Roadmap Phase 3 的"harder opponents"建议**前移到 Phase 2 末尾**,而不是单 Easy AI 撞 50%
- 训练框架第一天就为对手池预留接口(类比 MacroGym 的 `AGENT_REGISTRY`)——回头补改动很大
- 自博弈 checkpoint 池放 Phase 4/5 没问题,**规则 baseline 的对手池要尽早**

### 2.5 战争迷雾(POMDP)按显式处理,不要装作 MDP

MacroGym v2 之前把对手所有信息塞 obs,agent 在"完美信息"下学的策略,
切到 POMDP 上线立刻崩。v2 加显式 FogTracker(scout 快照 + 接触刷新)之后,agent 学会了主动侦察。

对 RA2_RL:
- 红警 2 自带战争迷雾,**不要绕过它喂 ground truth 给 agent**
- obs 里"看不见的敌方单位"应是过去某时刻的快照,带时间衰减
- 值得开一个 ADR

### 2.6 评估必须用对手矩阵,不能单点

MacroGym 循环赛(7 agent × 双向 10 局 = 140 局)发现了单挑看不出来的问题——
dawn-PPO-v1 对 economic 100% 赢但对 aggressive 只有 30%。

对 RA2_RL:
- Phase 2 验收 "> 50% vs Easy AI" 是**最低门槛**,不是充分条件
- 一开始就把 `tournament.py` 等价物搭起来,所有训练成果过同一套循环赛
- 出 heatmap + build-order timing 图——比 reward curve 信息密度高得多

## 3. 工程实践(可直接抄)

### 3.1 Agent 接口要早定下来

MacroGym 的 `agent(me, opp, besieged=False) -> action_id` 协议让规则 agent 和 RL agent 完全互换,
arena / tournament / 录像跑同一接口。

对 RA2_RL:Phase 1 第一周就定接口,例如

```python
class Agent(Protocol):
    def reset(self, env_info: dict) -> None: ...
    def act(self, obs: np.ndarray, mask: Optional[np.ndarray]) -> int: ...
```

让规则 agent / SB3 PPO / 外部模型走**同一接口**。

### 3.2 对战擂台 + 录像作为一等公民

MacroGym 的 `arena.py` + `record_match.py` 让每个 checkpoint 立刻能跑对战 + 出 mp4,
报告/演示阶段直接救命。RA2_RL 录像更便宜(游戏自带 replay / 直接录屏),
但**评估擂台**还是要单独写。

### 3.3 数据与可视化分离

`tournament_results.json` → `tournament.py --chart` 出图。
**所有图表从 JSON 重生**,不要把数字写死在画图代码里。
RA2_RL 训练成本高,一次跑出来的数据要能反复出图。

### 3.4 不要 mock 环境

MacroGym 早期写过假 env 做单元测试,后来 mock 和实际行为差距越来越大,
最后所有测试改成跑真 env。

对 RA2_RL:
- `RA2Env` 的测试用真游戏跑,不要 mock 内存读取
- 这条和 ADR-0004(纯净版 YR)叠加意味着:**Phase 0 不通过,Phase 1 一行代码都不要写**

## 4. MacroGym 没回答、RA2_RL 必须自己回答的问题

| 问题 | MacroGym 状态 | RA2_RL 怎么办 |
|---|---|---|
| 空间/位置 | 无,单位抽象为"我方/敌方"两集合 | 2D 地图;Phase 3 上 spatial feature map + Transformer |
| 多兵种异质性 | 只有"坦克" | 十几种;Phase 1 只考虑核心几种(犀牛/光棱/天启),其余忽略 |
| 建造队列 | 即时造单位 | 有队列/暂停/退款;Phase 1 简化为"加入队列即视为造出" |
| 多线作战 | 三阶段显式建模 | 真实多线无显式阶段,靠 agent 学;reward 不再人为分阶段 |
| 训练 wall time | 一次 < 4 小时 | 估计 10–100 倍——**Phase 1/2 的迭代速度是项目最大风险** |

## 5. 对 RA2_RL Roadmap 的两点优先级调整建议

1. **Phase 1 末尾加"对战擂台 + 录像"**:Phase 1 结束时除"随机 agent 跑 100 局不崩"外,
   还有一个能给两个 agent 对战出 mp4 的工具。Phase 2/3 都要用,**早做收益大**。
2. **Phase 2 的对手池在 Phase 1 末尾就开始攒**:哪怕只是写死的"造兵海"规则 agent。
   Phase 2 训练 PPO 时直接用,避免 Easy AI 单点过拟合。

## 6. 一句话总结

> RA-MacroGym 留下的不是代码,是一份**已经验证过的 RL 项目流程清单**:
> PPO + VecNormalize + 显式 POMDP + reward shaping 迭代 + 对手池 + 循环赛评估 + Agent 接口协议。
> RA2_RL 不必重新发现这些。

---
基础项目:CA6126 final project (RA-MacroGym v2.2)
