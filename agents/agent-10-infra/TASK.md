# Agent-10 · 测试/CI/工程基础设施

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-10 | **模块**：横向基础设施——单测收编、CI、依赖管理、仓库卫生
- **工作区**（独占写）：`agents/agent-10-infra/`
- **名下主树文件**（独占写）：`tests/`（已收编的测试）、`pyproject.toml`、`.github/workflows/ci.yml`、`requirements/`（拆分后的依赖清单目录）
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`

## 项目背景

10 个 Agent 并行开发，最大的工程风险不是写不出代码，而是**集成时互相踩**。你是全队的质量底线：统一测试框架与跑法、CI 在每次 push 时守住主树、依赖清单从「口头通报」变成「文件为准」。你自己的业务代码很少，价值全在让其他 9 个人的产出可靠合流。

## 任务目标

1. **测试基建**（`pyproject.toml` + `tests/`）：
   - `pyproject.toml`：pytest 配置——marker 定义 `unit`（纯逻辑，无外部依赖）/ `integration`（需 Docker server）/ `trackb`（需真实游戏，仅 venv B）；默认只跑 `unit`；
   - `tests/` 骨架：`conftest.py` 放共享 fixture（mock OpenEnv observation model 工厂——各 Agent 单测都要造 obs，一个工厂服务全队，与 Agent-02 的 obs_schema.md 对齐）；
   - **收编流程**：各 Agent 集成时把工作区 `tests/` 复制进主树 `tests/`（他们自己 commit），你负责审查命名/覆盖/标记是否合规——发现不合规在 BOARD 广播，**不直接改别人测试**。
2. **CI**（`.github/workflows/ci.yml`）：
   - 触发：push/PR 到 main；跑 `pytest -m unit` + ruff（若引入则 `--fix` 不开，只报）；
   - runner：`windows-latest` + Python 3.10（对齐 venv A；纯单测不依赖 Docker/游戏，标记隔离保证 CI 可跑）；
   - 失败通知：workflow 徽章挂 README（README.md 的 Status 区加一行——README 归主项目，通过 BOARD 提案让主项目改，或你在提案确认后改，改前走广播流程）。
3. **依赖拆分**（`requirements/`）：
   - `requirements-track-a.txt`（openra-rl 0.4.1、gymnasium、numpy<2.3、sb3、tensorboard…以 BOARD 通报为准冻结版本）
   - `requirements-track-b.txt`（pyra2yr 0.3.0、numpy<2.0，注明 Python ≥3.11）
   - 根 `requirements.txt` 改成两行注释指向上述文件（**根 requirements.txt 归你改**，在名下文件清单内追加即可，需 BOARD 提案一次）；
   - 每份文件头部注释写明对应 venv 路径与安装命令。
4. **make/脚本便利层**（可选加分）：`scripts/dev.ps1` 或 `make`——`test`（unit）/ `test-all` / `lint` / `server-up`（调 05 的 health）。别过度工程，一个入口文件即可。
5. **仓库卫生巡查**：定期 `git status` 巡查未登记文件、`.gitignore` 漏网（如新的二进制产物类型），发现即在 BOARD 广播。

## 技术要点

- CI 里 **绝不** 跑 integration/trackb（无 Docker/游戏）：靠 marker 隔离，conftest 里对缺依赖的 marker 做 skip 兜底。
- 收编测试时不修复、不重构他人测试——合规审查只看：命名规范（`test_<模块>_<行为>.py`）、marker 正确、不依赖网络/游戏、断言有信息量。
- ruff 先只开默认规则集（E/F），不搞全家桶；pyproject 里配置好排除 `Ra2Game412*/` `third_party/`。
- 单测要快：CI 目标 < 2 分钟；慢测试标 integration。

## 接口契约（v1 冻结）

- **你依赖**：无阻塞依赖；fixture 工厂参考 Agent-02 的 obs_schema.md（他公布前先用 a2 脚本字段自造 v0）。
- **被依赖**：全队（测试跑法、CI 红灯、requirements）。
- CI 首次上线后在 BOARD 广播「红灯规则」：CI 失败 = 相关集成回滚或 24h 内修复。

## 验收标准（DoD）

- [ ] `pytest -m unit` 一条命令可跑、markers 生效
- [ ] CI 上线并在后续 push 中真实执行（含徽章提案）
- [ ] requirements 两轨拆分完成、版本以 BOARD 通报冻结
- [ ] 名下文件已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
