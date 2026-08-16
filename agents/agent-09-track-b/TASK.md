# Agent-09 · 线路 B 原版保真旁路

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-09 | **模块**：ra2yrcpp/pyra2yr 旁路——原版保真验证与录像
- **工作区**（独占写）：`agents/agent-09-track-b/`
- **名下主树文件**（独占写）：`scripts/trackb/`（整个子目录）
- **Python 环境**：**venv B** — `E:\conda_envs\ra2rl-b\Scripts\python.exe`（Python 3.11，pyra2yr 0.3.0）。**与 venv A 不可混用（numpy 版本冲突）**。

## 项目背景

ADR-0005（Accepted）：训练主路是 OpenRA-RL，但 ra2yrcpp 是唯一跑在**原版二进制**上的路线，承担「原版保真验证 + 录像录制」，也是未来对接中国对战平台的底座。Phase 0 已跑通：补丁版 spawner → pyra2yr 连 `127.0.0.1:14521` 逐帧读状态 → 指令下发 → 完整 episode。你的任务把 Phase 0 的验证脚本升级为**可复用的工具层**。

必读：`scripts/gen_spawn_b3.py`、`scripts/b4_connect_test.py`、`scripts/b5_command_test.py`、`docs/roadmap.md` 线路 B 踩坑记录（5 条全读）。

## 任务目标

1. **`scripts/trackb/spawn_config.py`**：对局配置生成器——扩展现有 `gen_spawn_b3.py`：参数化对手数量/难度、地图（从 `Ra2Game412-rl\Maps\` 枚举可选）、玩家阵营/颜色/位次；`MultiGameInstanceConfig` → `spawn.ini` + `spawnmap.ini`；CLI：`python spawn_config.py --map X --difficulty easy --out <dir>`。
2. **`scripts/trackb/pyra2yr_adapter.py`**：同步适配层——
   - `PyRA2Client(host, port=14521)`：connect / `get_state()`（容忍加载期 None，参考 b4 的 monkeypatch 方案）/ `send_commands(cmds)` / `wait_episode_end(timeout)`；
   - 目标形态对齐 OpenEnv 概念（state → observation 字段子集），为保真对比铺路；
   - 所有等待函数带 timeout 与明确异常。
3. **`scripts/trackb/fidelity_probe.py`**：保真对比探针——同一边界条件下分别从线路 A（OpenEnv obs）与线路 B（pyra2yr state）抽取对应字段（cash/power/单位计数/建筑计数/tick），输出映射表 `agents/agent-09-track-b/field_mapping.md`：字段对齐/单位对齐/量纲差异/无法对齐项。这是 ADR-0005 预言的「保真验证」首次落地，不求全，求建立**可持续对比的框架**。
4. **录像/回放调研**：工作区 `REPLAY_NOTES.md`——原版对局录制机制（ra2yrcpp 是否暴露 replay 接口、spawn 模式的录像文件、或状态流录制回放方案）调研结论与推荐路线，不写代码。
5. **运维纪律**（硬性）：每次真实游戏测试后清理 `gamemd*.exe` 进程（`taskkill /F /IM gamemd-spawn-ra2yrcpp.exe` 等，脚本里做成 finally/退出钩子）；只在 `Ra2Game412-rl/` 副本上操作；测试尽量批量少开窗（原版无 headless，窗口资源宝贵）。

## 技术要点（Phase 0 已知坑，直接继承）

- `pyra2yr.Game` 启动器 Windows 不可用——手动启动 `Ra2Game412-rl\gamemd-spawn-ra2yrcpp.exe -SPAWN`，pyra2yr 只当客户端。
- `get_state()` 加载期返回 None 会崩 mainloop——b4 的 `StateManager.should_update` monkeypatch 方案照搬。
- 窗口化需 16 位色深；失焦自动最小化但局照常推进（可用挂机等待）。
- `ra2yrcpp.log` 的 `unknown TypeClass` 是噪声，不要浪费时间去修。
- 无人操作约 11500 frames（最快档约 3 分钟）一局，适合做端到端回归。

## 接口契约（v1 冻结）

- `scripts/trackb/` 内自包含（不 import venv A 的任何包）；与 01-08 的协作只通过 BOARD 与文档（field_mapping.md 是给 02/04 的参考资料）。
- spawn_config 生成的 ini **不进 git**（.gitignore 已挡 `*.ini`），生成目录用 `Ra2Game412-rl/` 内部或 `runs/`。

## 验收标准（DoD）

- [ ] spawn_config 可生成 ≥2 种难度 × ≥2 张地图的可用配置（实开一局验证）
- [ ] adapter 独立模块化，b4/b5 场景用 adapter 重写后行为不变（脚本级回归）
- [ ] field_mapping.md 首版（至少 cash/power/单位计数三项对齐）
- [ ] REPLAY_NOTES.md 有推荐结论
- [ ] 全程无残留 gamemd 进程（每次测试后自查并在 PROGRESS 记录）
- [ ] 名下文件已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
