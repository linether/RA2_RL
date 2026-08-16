# Agent-05 · 稳定性与崩溃恢复

> 启动顺序：`agents/README.md`（章程）→ 本任务书 → 自己的 `PROGRESS.md`。

## 你是谁

- **编号**：Agent-05 | **模块**：环境稳定性——server 健康、崩溃恢复、自动重启
- **工作区**（独占写）：`agents/agent-05-recovery/`
- **名下主树文件**（独占写）：`ra2_env/recovery.py`、`ra2_env/health.py`
- **Python 环境**：venv A — `E:\conda_envs\ra2rl\Scripts\python.exe`

## 项目背景

Phase 1 出口标准是「随机 Agent 连续跑 100 局不崩溃」——但现实是：Docker server 会挂、reset 60-120 秒会超时、episode 会异常终止。roadmap 明确列有「崩溃恢复与自动重启」条目。你提供两层能力：**事前保活**（server 健康检查与拉起）+ **事后兜底**（`SupervisedEnv` 包装 RA2Env，崩了自动重开 episode 并记账）。

必读：`docs/roadmap.md`（Phase 1 条目 + 线路 A 备注，Docker 镜像 0.4.1 tag 坑）、`docs/technical-notes.md`。

## 任务目标

1. **`ra2_env/health.py`**：
   - `is_server_up(base_url) -> bool`：探测 :8000 健康（HTTP 探活）。
   - `ensure_server(base_url, timeout=180.0) -> bool`（契约签名见章程 §5）：down 时调 `openra-rl server start` 拉起（subprocess，注意用 venv A 的可执行入口），轮询直到 healthy 或超时；处理 Docker Desktop 未启动（WSL2 backend，装在 `D:\DockerDesktop`）的场景——给出可操作的错误信息而不是堆栈。
   - `server_state() -> dict`：容器状态快照（`docker ps` 过滤 openra 容器），供诊断脚本与 metrics 用。
2. **`ra2_env/recovery.py`**：
   - `SupervisedEnv(gymnasium.Env)`：**组合包装** `inner_env`（即 Agent-01 的 RA2Env，构造注入，禁止修改其代码）。行为：
     - `step`/`reset` 抛异常（连接断、TimeoutError 等）时按策略恢复：小故障重试（指数退避，可配次数）→ 大故障 `ensure_server()` + 重建 inner_env → 恢复失败则向上抛 `RecoveryError`（带诊断上下文）。
     - episode 异常终止后自动 `reset()` 开新局，当前 episode 记为 crash；`info["restarts"]` / `info["crash"]` 透出。
     - 恢复预算：`max_restarts_per_episode`、`max_total_restarts`，超预算停机（防死循环）。
   - `RecoveryLog`：JSONL 事件流（时间戳/事件类型/重试次数/容器状态），写到 `runs/recovery/`（已 gitignore）；会话结束输出摘要（crash 率、MTBF）。
3. **诊断脚本**：工作区 `chaos_test.py`——主动杀容器（`docker stop`）验证 SupervisedEnv 能拉起重来；`health_cli.py` 手动查 server 状态。
4. **单测**：mock inner_env（注入抛异常序列）覆盖：一次故障一次恢复、预算耗尽、close 幂等、重试退避节奏。放工作区 `tests/`，交 Agent-10 收编。

## 技术要点

- 与 Agent-01 的边界：他负责把错误抛清楚（如 server 未启动时明确报错），你负责接住并恢复。**不要**往他的 env.py 里加 try/except——包装层做所有事。
- reset 慢（60-120s）是常态不是故障：超时阈值要区分「首次 reset 冷启动」与「step 中卡死」。
- Windows 下 subprocess 启动 `openra-rl` CLI：确认 PATH/入口解析方式（`E:\conda_envs\ra2rl\Scripts\openra-rl.exe`），Docker Desktop 未跑时先起 Docker Desktop 或给出明确指引。
- 并发注意：Agent-06 压测与 Agent-07 训练都包你的类，恢复路径必须线程安全（至少说明单线程假设）。

## 接口契约（v1 冻结）

```python
class SupervisedEnv(gymnasium.Env):
    def __init__(self, inner_env, max_retries: int = 3, backoff_base: float = 2.0,
                 max_restarts_per_episode: int = 2, max_total_restarts: int = 50,
                 log_dir: str | None = None) -> None: ...

def ensure_server(base_url: str = "http://localhost:8000", timeout: float = 180.0) -> bool: ...
```

- **你依赖**：Agent-01 的 RA2Env 集成后做真实联调（前期用 mock inner_env 开发）。
- **被依赖**：Agent-06（压测包你的类）、Agent-07（训练长期跑必须包）。

## 验收标准（DoD）

- [ ] chaos_test 实测：容器被杀后环境自动恢复并继续跑
- [ ] mock 单测全绿；恢复预算与记账行为正确
- [ ] `runs/recovery/` 事件流与摘要可用
- [ ] 已集成主树、登记 BOARD.md 集成表，PROGRESS.md 完整
