# Agent-06 · 随机 Agent 压力测试

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-06 | **模块**：随机 Agent + 压力测试（**Phase 1 验收的执行人**）
- **工作区**（独占写）：`agents/agent-06-random-agent/`
- **名下主树文件**（独占写）：`scripts/random_agent.py`、`scripts/stress_test.py`、`scripts/run_env_smoke.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`

## 项目背景

Phase 1 出口标准：**「随机 Agent 连续跑 100 局不崩溃」**（`docs/roadmap.md`）。你是这条标准的Owner——搭建可复现的压力测试体系，跑出证据，输出报告。同时你的压测会最先暴露 01（环境）/03（动作）/05（恢复）的集成 bug，是全链路的试金石。

## 任务目标

1. **`scripts/run_env_smoke.py`**：最小编成烟测试——构造 `RA2Env`（必要时包 `SupervisedEnv`），reset → 随机 20 步 → close，打印观测 shape/奖励序列/done。给所有 Agent 当「环境通不通」的 30 秒检查工具。
2. **`scripts/random_agent.py`**：随机策略库——均匀采样；可选 mask-aware 采样（用 Agent-03 的 `action_mask`，若提供）；固定 seed 可复现。CLI：`--episodes N --seed S --max-steps M --masked`。
3. **`scripts/stress_test.py`**：压测主入口——
   - 跑 N 局（默认 100），统计：完成局数 / crash 局数 / 自动恢复次数 / 平均局长（tick 与 step）/ 奖励分布（min/max/mean/σ）/ 动作分布（各 id 频次，暴露动作翻译失效）；
   - 中断保护：结果增量落盘 `agents/agent-06-random-agent/reports/stress_<date>.json`（进程死了已跑的不丢）；
   - 每局事件（restart/crash/异常 action）追加 JSONL；
   - 结束生成 markdown 报告 `reports/stress_<date>.md`：结论先行（通过/不通过 + 一句话原因），明细表在后。
4. **bug 上报闭环**：压测发现的环境/动作/恢复 bug 一律在 BOARD.md 广播区报告 Agent-01/03/05（署名、附最小复现），修复后回归。
5. **Phase 1 验收报告**：100 局达标后出正式报告（放工作区 `reports/phase1_acceptance.md`），在 BOARD 通知主项目。

## 技术要点

- **先骨架后实弹**：01/03/05 集成前，用工作区 mock env（契约同签名）把 harness 全部写好；他们一集成，直接切真实环境开跑。
- 依赖顺序：smoke → 单局全流程 → 10 局小压测（暴露问题）→ 100 局正式压测。不要一上来就跑 100 局。
- 一局很长（无操作 3000+ tick；`--max-steps` 截断保护必须有，默认参考 20000 步 = RA2Env 的 `max_episode_steps`）。
- 跑长测前 `ensure_server()`（Agent-05 的 health 模块，可先用自己的一行探活代替）。
- 报告里区分「环境崩溃」（crash/restart）与「游戏性截断」（truncated 到步数上限）——后者是正常现象不算失败。

## 接口契约（v1 冻结）

- 你的脚本 CLI 参数保持上述命名；`reports/` 目录仅在你工作区，产物小（json/md）可直接入库。
- **你依赖**：Agent-01（RA2Env）、Agent-03（动作清单与 mask）、Agent-05（SupervisedEnv）。
- **被依赖**：Agent-07/08 复用你的 harness 跑训练期评估；你的验收报告是 Phase 1 → Phase 2 的门禁。

## 验收标准（DoD）

- [ ] smoke 脚本 30 秒内给出环境健康结论
- [ ] 压测报告链完整（json + md，增量落盘验证过）
- [ ] 100 局压测通过或已出具带证据的不通过报告与 bug 清单
- [ ] 名下三脚本已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
