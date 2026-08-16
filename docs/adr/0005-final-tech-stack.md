# ADR-0005: 最终技术栈决定（双线验证后定稿）

## Status

**Accepted**(2026-06-11 定稿;2026-05-21 起草)— Phase 0 双线验证均通过,采纳预案 3

本 ADR **Supersedes ADR-0002 / Updates ADR-0004**,见末尾"Supersedes"。

## Context

ADR-0002 选择内存注入路线,ADR-0004 进一步约束开发环境必须是无补丁的纯净版 YR 1.001。
项目实际推进中遇到两个变化,迫使重新评估:

1. **纯净版 YR 1.001 的获取被证实是硬阻塞**:中国主流分发渠道
   (红警战网、平台版 `Ra2Game412/`)均带平台自有补丁,无合法公开渠道获取无补丁的
   1.001 安装包。
2. **2026-05 重新调研发现两个变量**(详见 `docs/research-report-2026-05.md`):
   - **ra2yrcpp 上游 2026-01 更新**:README 改为推荐 CnCNet YR client + Syringe +
     yrpp-spawner 组合,不再要求"完全纯净版";ADR-0004 的刚性约束可能已部分失效
   - **OpenRA-RL 0.4.1 横空出世**:`pip install openra-rl` 一行安装,
     OpenEnv 标准 Gym 接口、48 个 MCP 工具、Docker headless、64 局并发、活跃维护,
     完整覆盖 ADR-0002 之外的另一条路线 —— 基于 OpenRA 引擎的 RA2 重制,而非原版二进制

这两个变量共同导致原"内存注入唯一路线"假设需要重新审视。

## Decision Drivers

按重要性排序:

1. **能不能跑起来**:在不付出不合理代价(版权风险、不可逆环境改动)的前提下,
   能让 Gymnasium `env.step()` 真的转起来
2. **训练迭代效率**:headless、并发、崩溃恢复 —— 直接决定 Phase 2 训练周期
3. **原版保真度**:对最终能否部署到中国对战平台的影响
4. **维护风险**:上游消失、bug 修复响应、协议格式变化
5. **生态契合度**:与 SB3 PPO / VecNormalize / 对手池(`docs/lessons-from-macrogym.md`
   的经验)的集成成本

## Options(详见 `docs/research-report-2026-05.md`)

| 方案 | 引擎 | RL 适配 | Headless | 部署到对战平台 | 状态 |
|------|------|---------|----------|----------------|------|
| A: OpenRA-RL | OpenRA(C# 重制) | ⭐⭐⭐⭐⭐ OpenEnv | ✅ Docker | ❌ 引擎不同 | Phase 0 验证中 |
| B: ra2yrcpp + pyra2yr | 原版 gamemd.exe | ⭐⭐ 异步 API | ❌ 必须渲染 | ⚠️ 二进制差异 | Phase 0 验证中 |
| C/D: Chrono Divide / RA2Web | TS 重写/反编译 | ⭐ 无 Gym | ❌ 需浏览器 | ❌ | 拒绝(生态/法律) |
| E: 直接用 OpenRA RA2 mod | OpenRA | ⭐⭐ 需自建接口 | ✅ | ❌ | 拒绝(被 A 覆盖) |
| F: 屏幕捕获 + CV | 任何版本 | ⭐⭐⭐ | ⭐⭐ | ✅ | 兜底,不主推 |

## Phase 0 双线验证结果(2026-06-11,均通过)

**线路 A — OpenRA-RL** ✅
- `openra-rl 0.4.1` 装于 venv `ra2rl`(Python 3.10.18),`import openra_env` / `openra-rl doctor` 全绿
- Docker Desktop 装于 `D:\DockerDesktop`(WSL2 backend,数据 `D:\DockerData`)。镜像 `latest` tag 上游只推了 arm64,需拉 `0.4.1`(含 amd64)再本地 tag 成 latest
- `openra-rl server start` 容器 healthy(:8000);OpenEnv reset/step/观测/奖励流通过
- **完整 episode 闭环**:DEPLOY(mcv→fact)+ SURRENDER → `done=True / result='lose' / reward=-0.999`(`scripts/a3_surrender_test.py`)

**线路 B — ra2yrcpp + pyra2yr** ✅
- `pyra2yr 0.3.0` 装于 venv `ra2rl-b`(Python 3.11.15)
- 注入方式实际走 **Method 3 二进制补丁**(`patch_gamemd.py --auto-patch` 生成 `gamemd-spawn-ra2yrcpp.exe`),**无需 CnCNet client / Syringe / yrpp-spawner** —— 比起草时设想的更轻
- `gamemd-spawn-ra2yrcpp.exe -SPAWN` 注入 6 hook、:14521 监听;pyra2yr 逐帧读状态 + deploy 指令生效 + 完整 episode 自然结束(人类 defeated→EXIT_GAME)

两线均在 2026-06-11 跑通完整 episode,**预案 4(回退屏幕捕获)排除**。

## Decision:预案 3(双线并存)

**训练环境用 OpenRA-RL**(headless / Docker / 可并发 / OpenEnv 标准接口 / 社区活跃),
**保留 ra2yrcpp + pyra2yr 作为"原版保真验证 + 录像录制"工具**,
部署到中国对战平台留待 Phase 5 独立适配(可能借助方案 F 屏幕捕获)。

理由:线路 A 的 headless + 并发 + 标准 Gym 接口直接决定 Phase 2 训练迭代效率(Decision Driver #2),
是训练主路;线路 B 虽必须开真实窗口、并行度受限,但它是唯一在**原版二进制**上运行的路线,
对最终部署保真度(Driver #3)有不可替代的价值,作为旁路保留成本很低(独立 venv)。

**对比起草时的预期修正**:线路 B 的注入门槛比 ADR-0004 担心的低得多——二进制补丁法不依赖
纯净版 1.001,也不需要 CnCNet client,平台版 `Ra2Game412/` 的 `gamemd-spawn.exe` 直接可补丁。
ADR-0004"必须纯净版"的刚性约束因此降级为"测试用纯净副本目录"的工程惯例。

## Consequences

- 训练主路定为 OpenRA-RL:`README.md` / `docs/architecture.md` 的"YR 原版"语言需标注
  "训练引擎为 OpenRA RA2 重制,原版保真由线路 B 旁路保证";观测/动作空间按 OpenEnv 接口写
- `requirements.txt` 两套(`ra2rl` 留 openra-rl,`ra2rl-b` 留 pyra2yr),因 Python/numpy 版本不相容必须分 venv
- Phase 1 `RA2Env`:**先封装 OpenRA-RL 的 OpenEnv→Gymnasium**(异步 client 已是现成的 reset/step);
  pyra2yr 的异步→同步适配层延后到需要原版验证时再做
- `docs/adr/README.md` 标 ADR-0005 Accepted,ADR-0002 Superseded,ADR-0004 Updated

## Supersedes / Updates

- **Supersedes ADR-0002**:训练路线从"原版内存注入唯一"改为"OpenRA-RL OpenEnv 为主,
  ra2yrcpp 内存注入为原版保真旁路"
- **Updates ADR-0004**:"必须无补丁纯净版 YR 1.001"降级为"线路 B 测试用纯净副本目录"的工程惯例,
  不再是硬约束(二进制补丁法对平台版 spawner 即可工作)

## References

- `docs/research-report-2026-05.md` — 6 方案完整对比
- `docs/lessons-from-macrogym.md` — 来自 RA-MacroGym 的设计经验(任一路线都适用)
- ra2yrcpp Release:https://github.com/shmocz/ra2yrcpp/releases/download/latest/ra2yrcpp.zip
- pyra2yr Release:https://github.com/shmocz/pyra2yr/releases/download/v0.3.0/pyra2yr-0.3.0-py3-none-any.whl
- OpenRA-RL:https://github.com/yxc20089/OpenRA-RL
