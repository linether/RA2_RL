# Agent-08 · 评估体系

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-08 | **模块**：评估与对战分析（Phase 2 门禁的度量者）
- **工作区**（独占写）：`agents/agent-08-evaluation/`
- **名下主树文件**（独占写）：`eval/evaluate.py`、`eval/metrics.py`、`eval/__init__.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`（可选 `pip install matplotlib`，版本报 BOARD）

## 项目背景

Phase 2 出口标准是「PPO Agent vs Easy AI 胜率 > 50%（固定地图）」——没有可信、可复现的评估体系，这条标准无法裁决。你提供：确定性评估协议（固定 seed、固定局数）、指标集（胜率只是其一）、对比报告（checkpoint 间/对基线）。评估既独立 CLI 运行，也作为 Agent-07 训练中的 EvalCallback 后端。

## 任务目标

1. **`eval/metrics.py`**——契约签名（章程 §5）：`evaluate(policy, env, n_episodes, seed=0) -> dict`：
   - `policy`：SB3 模型或任意 `callable(obs) -> action_id`（随机策略、脚本策略都能评——降级友好）；
   - 输出指标 dict：`win_rate / draw_rate / lose_rate / mean_reward / mean_ep_length (steps+ticks) / action_distribution / economy_curve_summary（cash 峰值与终值均值）`；
   - seed 严格传递 env.reset(seed=...)（RA2Env 若暂不支持，BOARD 与 01 对齐补上；评估的可复现性优先级高于 convenience）。
2. **对手与场景控制**：调查 OpenEnv reset 的可配项（对手难度/地图/阵营——server 场景怎么配），结论写工作区 `SCENARIOS.md` 并在 BOARD 公布。至少支持「固定地图 + Easy AI」基准场景；若难度暂不可配，记录现状并定义可用的最接近基准。
3. **`eval/evaluate.py`**：CLI——
   - `--model <path.zip | random | script:xxx>` + `--episodes N --seed S --scenario easy-fixed`；
   - 支持多 checkpoint 对比：`--model a.zip b.zip c.zip` 输出对比表（胜率±置信区间、净奖励、局长）；
   - 输出：`agents/agent-08-evaluation/reports/eval_<date>.md`（结论先行）+ 同名 json；附可选 matplotlib 曲线图（cash/reward over ticks，失败不阻塞）。
4. **统计纪律**：胜率必须附区间（Wilson 或正态近似，注明局数）；报告注明 config/commit/seed，保证第三方可复跑。
5. **冒烟**：mock policy + mock env 全流程；01 集成后跑 `random vs Easy AI` 10 局基线（这组数字是 Phase 2 的对照组，价值高，PROGRESS 里高亮）。

## 技术要点

- 与 06 的边界：他做**环境稳定性压测**（随机策略、看崩不崩），你做**策略质量评估**（谁赢、赢多少）；harness 互相参考不互相依赖，evaluate() 的实现保持无状态纯函数。
- episode 长且 reset 慢：评估串行即可（N 局 × 2-5 分钟），并发留 Phase 4；进度条/增量落盘要有。
- 动作分布指标能提前暴露「策略坍缩到 NOOP」——这是 Phase 2 最常见的死法，务必保留。
- policy 加载失败/环境崩溃的降级路径写清楚（评估中途崩了：已完成局保留，报告标注中断原因）。

## 接口契约（v1 冻结）

```python
# eval/metrics.py
def evaluate(policy, env, n_episodes: int, seed: int = 0) -> dict: ...
```

- **你依赖**：Agent-01（RA2Env reset 的 seed 支持）、Agent-07（模型格式，SB3 load 即可）；mock 期无依赖。
- **被依赖**：Agent-07（EvalCallback 调你的 evaluate）。

## 验收标准（DoD）

- [ ] evaluate() 契约一致、无状态、mock 全流程绿
- [ ] `SCENARIOS.md` 记录场景可控性结论
- [ ] `random vs Easy AI` 基线数据出具（01 集成后）
- [ ] 名下文件已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
