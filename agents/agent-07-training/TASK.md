# Agent-07 · SB3/PPO 训练集成

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-07 | **模块**：训练层——SB3 PPO 管线（Phase 2 前置基建）
- **工作区**（独占写）：`agents/agent-07-training/`
- **名下主树文件**（独占写）：`train/train_ppo.py`、`train/config.py`、`train/__init__.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`
- **新依赖**：`pip install stable-baselines3 tensorboard`（装完把包名+版本报 BOARD 广播区，Agent-10 收编 requirements）

## 项目背景

Phase 2 目标是「PPO 基线击败原版 Easy AI」（`docs/roadmap.md`）。你现在把训练管线搭好并进入 Phase 1→2 过渡：环境没就绪时用 mock env 把管线全链路打通（VecNormalize 统计量、checkpoint、TB、eval 回调），环境一集成即可开训。参考 `docs/adr/0003-single-agent-ppo-baseline.md`（单 Agent PPO 决策）与 `docs/lessons-from-macrogym.md`（对手池等经验，Phase 2 后期用）。

## 任务目标

1. **`train/config.py`**：`TrainConfig` dataclass——PPO 超参（n_steps/batch_size/gamma/gae_lambda/ent_coef/lr/n_epochs…）、环境参数（base_url/max_episode_steps）、训练预算（total_timesteps）、路径（checkpoint/TB 目录）、eval 设置（频率/局数/seed）。支持从 Python dict / JSON 文件加载（`--config train/configs/baseline.json`），内置 `DEFAULT_BASELINE`（给量级理由的注释）。
2. **`train/train_ppo.py`**：CLI 主入口——
   - 构造 env：`RA2Env`（Agent-01）→ 必要时包 `SupervisedEnv`（Agent-05）→ `Monitor` → `DummyVecEnv`；
   - `VecNormalize`（norm obs+reward，clip 10，γ=0.99）：训练结束保存 `vecnormalize.pkl`，断点续训时加载——checkpoints 目录已 gitignore，路径写进运行清单；
   - PPO：`TensorBoard` 日志到 `runs/tensorboard/`；`CheckpointCallback` 每 N 步存 `checkpoints/`；`EvalCallback` 挂 Agent-08 的 evaluate（未集成前用内置评估回调，集成后切换，BOARD 协调）；
   - 断点续训：`--resume <checkpoint.zip>` 加载模型 + VecNormalize 统计量 + 步数计数；
   - 课程表钩子：回调里按训练进度调 `weight_schedule`（Agent-04）更新 reward 权重（通过 env 属性注入，具体机制与 01/04 在 BOARD 对齐；没就绪前留接口 + 注释）。
3. **短训验证**：mock env（同契约签名、合成奖励）跑通 `1e5` 步：loss 下降、TB 曲线存在、checkpoint 可 resume、VecNormalize 统计量正确演化。真实环境可用后（01/05 集成）跑 `1e4` 步冒烟并在 PROGRESS 记录结果。
4. **训练运行清单**：工作区 `RUNS.md`——每次训练记录：config 来源 / commit hash / 步数 / 结果指针（TB 路径、最佳 checkpoint）——保证实验可追溯。

## 技术要点

- mock env 要像样：观测维度用 Agent-02 的契约（先按他 BOARD 上公布的维度做常量，可后调）；奖励给可学习的合成结构（如线性可控量），验证的是**管线**不是策略。
- SB3 与 Gymnasium API 版本配套：确认 venv A 里 gymnasium 版本与 SB3 兼容（报给 10 收编）。
- 一局 60-120s reset + 长局：训练吞吐瓶颈在环境不在 GPU，`n_envs` 并行（SubprocVecEnv）留作 Phase 4，现在 DummyVecEnv + 说明即可。
- 环境崩了别炸训练：只包 SupervisedEnv，不要在 train_ppo.py 里 catch 环境异常。

## 接口契约（v1 冻结）

- **你依赖**：Agent-01（RA2Env）、Agent-05（SupervisedEnv）、Agent-04（weight_schedule）、Agent-08（evaluate，可后切）。
- **被依赖**：Agent-08（评估你的 checkpoint）、Agent-06（复用 harness 思路互不阻塞）。
- mock 期所有依赖以 stub 顶替，集成顺序在 BOARD「主树集成登记」跟踪。

## 验收标准（DoD）

- [ ] `train_ppo.py --config` 全流程在 mock env 跑通：TB/checkpoint/resume/VecNormalize
- [ ] 真实环境 `1e4` 步冒烟通过（01/05 集成后）
- [ ] RUNS.md 追溯链完整；依赖版本已通报 BOARD
- [ ] 名下文件已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
