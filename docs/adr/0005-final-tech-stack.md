# ADR-0005: 最终技术栈决定（双线验证后定稿）

## Status

**Proposed** — 决议待 Phase 0 双线验证完成后定稿(2026-05-21 起草)

本 ADR 一旦 Accept,**将超越/部分推翻 ADR-0002 与 ADR-0004**,见末尾"Supersedes"。

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

## Phase 0 双线验证当前进展(2026-05-21)

**线路 A — OpenRA-RL**
- ✅ `openra-rl 0.4.1` 装于 venv `ra2rl`(Python 3.10.18)
- ✅ `import openra_env`、`openra-rl doctor` 通过
- ⏳ Blocker:Docker Desktop 未安装 → 无法跑 `openra-rl play`

**线路 B — ra2yrcpp + pyra2yr**
- ✅ `pyra2yr 0.3.0` 装于 venv `ra2rl-b`(Python 3.11.15)
- ✅ `ExManager`、`ra2yrproto` import 通过
- ⏳ Blocker:CnCNet YR client + ra2yrcpp.zip + Syringe.exe 未到位 → 无法注入

任一线先通过,该线即为本 ADR 的 Decision。两线并行不冲突(分属不同 venv,
依赖不相容但分隔)。

## Decision(待定)

**预案 1(若线路 B 先通)**:采纳 ra2yrcpp + pyra2yr,但 ADR-0004 的"必须纯净版 1.001"
约束改为"CnCNet YR client + Syringe + yrpp-spawner 组合即可"。
ADR-0002 维持不变(内存注入路线)。

**预案 2(若线路 A 先通)**:采纳 OpenRA-RL 作为训练环境,**承认引擎不再是原版 YR**,
ADR-0002 部分作废(改为"基于 OpenRA 引擎的 RA2 重制"),ADR-0004 彻底作废。
部署到中国对战平台改为后期 Phase 5 的独立适配问题(可能借助方案 F 屏幕捕获)。

**预案 3(两线都通)**:训练用 OpenRA-RL(headless / 并发 64 局 / 跨平台 / 社区活跃),
保留 ra2yrcpp 作为"原版保真验证 + 录像录制"工具,部署还是看 Phase 5。

**预案 4(两线都不通)**:回退到方案 F 屏幕捕获 + CV(代价高,迭代慢,
但兼容性最好)。立项条件:线路 A 与线路 B 均在 2026-06 月底前无法跑通一次完整 episode。

## Consequences

待 Decision 定稿后填写。预期需修订的下游内容:

- 若选预案 2:`README.md`、`CLAUDE.md`、`docs/architecture.md` 需把"YR 原版"语言
  改为"OpenRA RA2 mod",观测/动作空间章节按 OpenRA-RL 的 OpenEnv 接口重写
- `requirements.txt` 按选定路线改:留 `openra-rl` 或 留 `pyra2yr` 安装链接
- `ra2_env/` 设计取决于路线:OpenEnv wrapper vs 自建 pyra2yr 异步→同步适配层
- `docs/adr/README.md` Index 更新本 ADR 状态,并对 ADR-0002/0004 标 Superseded 或 Updated

## Supersedes / Updates(预填,待 Decision 定后激活)

- 若选预案 2:**Supersedes ADR-0002**(改为 OpenRA-RL OpenEnv 接口)、
  **Supersedes ADR-0004**(无纯净版要求)
- 若选预案 1:**Updates ADR-0004**(约束放宽到 CnCNet client)

## References

- `docs/research-report-2026-05.md` — 6 方案完整对比
- `docs/lessons-from-macrogym.md` — 来自 RA-MacroGym 的设计经验(任一路线都适用)
- ra2yrcpp Release:https://github.com/shmocz/ra2yrcpp/releases/download/latest/ra2yrcpp.zip
- pyra2yr Release:https://github.com/shmocz/pyra2yr/releases/download/v0.3.0/pyra2yr-0.3.0-py3-none-any.whl
- OpenRA-RL:https://github.com/yxc20089/OpenRA-RL
