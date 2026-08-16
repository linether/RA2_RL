# Roadmap

## Phase 0 — Environment Validation（线路 B 已达成，2026-06-11 更新）

**目标：** 双线验证 OpenRA-RL 和 ra2yrcpp 两条技术路线的可行性。

### 线路 B — ra2yrcpp 原版注入 ✅ **2026-06-11 全线打通**
- [x] 创建 Python 3.11 venv (`E:\conda_envs\ra2rl-b`,Python 3.11.15)
- [x] `pip install pyra2yr 0.3.0`(含 `ra2yrproto` protobuf 绑定)
- [x] 纯净测试目录 `Ra2Game412-rl\`(从 `Ra2Game412` 复制,移除 Ares/Phobos 系)
- [x] ra2yrcpp release(commit `ee215f5`,2026-01-11)部署:`libra2yrcpp.dll` + `zlib1.dll` + `ra2yrcpp.json`(port 14521);zip 备份在 `third_party/`
- [x] 注入方式:**Method 3 二进制补丁**(非 Syringe)— `scripts/patch_gamemd.py --auto-patch` 生成 `gamemd-spawn-ra2yrcpp.exe`(addscn 加 `.p_text2` 段)
- [x] 遭遇战配置:pyra2yr `MultiGameInstanceConfig.to_ini()` 生成 `spawn.ini`(1 human + 1 AI),`arctic_circle.map` → `spawnmap.ini`(见 `scripts/gen_spawn_b3.py`)
- [x] 启动 `gamemd-spawn-ra2yrcpp.exe -SPAWN`:6 hook 全部创建,端口 14521 监听
- [x] pyra2yr 连通:逐帧读 state(frame/金钱/电力/单位数/defeated),frame 42→11530 全程稳定(`scripts/b4_connect_test.py`)
- [x] 指令下发:deploy MCV → frame 55 出现 conyard(`scripts/b5_command_test.py`)
- [x] **完整 episode:开局→逐帧状态→人类玩家 defeated→STAGE_EXIT_GAME→进程退出** ✅

### 线路 A — OpenRA-RL 快速验证
- [x] venv `E:\conda_envs\ra2rl`(Python 3.10.18),openra-rl 0.4.1 装好
- [x] Docker Desktop 装至 `D:\DockerDesktop`(WSL2 backend,数据在 `D:\DockerData`,不占 C 盘)
- [x] `openra-rl doctor` 全绿(Docker CLI + daemon + Python)
- [x] 游戏镜像:`latest` tag 只有 arm64(上游推坏了)→ **拉 `0.4.1` tag(有 amd64)本地 tag 成 latest** 绕过
- [x] `openra-rl server start`:容器 healthy,端口 8000
- [x] OpenEnv 接口验证:reset + step + 观测/奖励流稳定(`scripts/a2_episode_test.py`)
- [x] **完整 episode 闭环**:DEPLOY 指令(mcv→fact 建筑)+ SURRENDER → `done=True / result='lose' / reward=-0.999`(`scripts/a3_surrender_test.py`)✅
- [ ] 评估观测空间/动作空间对 RL 训练的适配度
- [ ] 测试 headless 并行训练性能

**线路 A 备注:** 无操作时一局很长(3000 tick 分不出胜负);用 SURRENDER 动作可确定性结束 episode。21 种 ActionType(move/attack/build/train/deploy/sell/place_building/set_stance/surrender…),观测含经济/军事/单位列表/spatial tensor(base64 float32 H×W×C)/win-lose-draw result。

**Python 环境备注:** 两条线 Python 版本要求冲突
- 线路 A 用 `E:\conda_envs\ra2rl`(Python 3.10.18,numpy 2.2.6)
- 线路 B 用 `E:\conda_envs\ra2rl-b`(Python 3.11.15,numpy 1.26.4)
- pyra2yr 要求 Python ≥3.11 且 numpy <2.0,无法与 openra-rl 共存
- venv 的 python 在 `Scripts\python.exe`(不是 conda 布局)

**线路 B 踩坑记录(2026-06-11):**
1. pyra2yr 的 `Game` 启动器只支持 Docker/Wine,Windows 上需手动启动补丁版 spawner,pyra2yr 仅作客户端
2. pyra2yr 0.3.0 bug:`get_state()` 超时(游戏加载中属正常)返回 None 会令 mainloop 崩溃 → 测试脚本里 monkeypatch `StateManager.should_update` 容忍 None
3. 游戏窗口化需 16 位色深(报"本產品需要 16 位元色盤"),目录无 cnc-ddraw 的 ddraw.dll 时只能全屏;失焦自动最小化但对局照常推进
4. `ra2yrcpp.log` 大量 `unknown TypeClass: 10/14/18/28` 为 state parser 噪声,不影响状态读取与指令
5. 无人操作时 AI 会平推人类玩家,一局约 11500 frames(游戏速度最快档约 3 分钟)自然结束 — 不是 bug

**Exit criteria：** ~~确定最终技术路线~~ → **线路 B 已跑通完整 episode,Phase 0 达成**;ADR-0005 定稿中(按线路 A 长跑结果选预案 1 或 3)。

## Phase 1 — Minimal Gym Environment

**目标：** 可运行的 Gymnasium 环境，支持随机 Agent 完整跑完一局。

- [ ] 实现 `RA2Env` 核心类（`reset` / `step` / `close`）
- [ ] 实现最小观测空间（扁平向量）
- [ ] 实现最小动作空间（10-15 个离散动作）
- [ ] 实现基础奖励函数
- [ ] 崩溃恢复与自动重启
- [ ] 随机 Agent 压力测试

**Exit criteria:** 随机 Agent 连续跑 100 局不崩溃。

## Phase 2 — Baseline Agent

**目标：** PPO 基线击败原版 Easy AI。

- [ ] Stable Baselines 3 集成
- [ ] 训练配置与超参数
- [ ] TensorBoard 监控
- [ ] 奖励 shaping 迭代
- [ ] 评估脚本

**Exit criteria:** PPO Agent vs Easy AI 胜率 > 50%（固定地图）。

## Phase 3 — Observation & Action Enrichment

**目标：** 支持更复杂的策略学习。

- [ ] 添加空间特征图（minimap grid）
- [ ] 添加实体列表与 Transformer encoder
- [ ] 扩展动作空间（建筑放置、编队控制）
- [ ] Action Masking
- [ ] 更高难度对手

**Exit criteria:** Agent 展现出超越 Tank Rush 的策略多样性。

## Phase 4 — Infrastructure Hardening

**目标：** 支持规模化训练。

- [ ] Docker 容器化（考虑 Wine headless 或 Windows Server）
- [ ] 并行环境（SubprocVecEnv 或 Ray）
- [ ] Checkpoint 管理与断点续训
- [ ] 崩溃自动恢复增强

## Phase 5 — Advanced Architecture

**目标：** 探索高级 RL 技术。

- [ ] 分层 Agent（Macro + Micro）
- [ ] 自我博弈（current vs historical checkpoints）
- [ ] 部署适配（训练环境 → 对战平台）
