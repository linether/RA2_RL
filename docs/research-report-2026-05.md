# 技术方案深度调研报告

> 调研日期：2026-05-18
> 项目：RA2_RL — 基于强化学习的红警2 AI 训练框架

---

## 一、背景与问题

RA2_RL 项目原定方案为 **ra2yrcpp + pyra2yr（内存注入）**，通过 DLL 注入纯净版 YR 1.001 的 `gamemd.exe` 获取结构化游戏状态，封装为 Gymnasium 环境后使用 PPO 训练。

**当前阻塞点：** 需要纯净版 YR 1.001（不含 Ares/Phobos 等社区补丁），而国内常见的红警安装包（如红警战网版 `Ra2Game412/`）均包含平台自有补丁，无法用于 `ra2yrcpp` 注入。

本报告调研了 6 条可选技术路线，从可行性、成熟度、RL 适配性等维度进行对比分析，为项目方向调整提供决策依据。

---

## 二、方案逐一分析

### 方案 A：ra2yrcpp + pyra2yr（原方案，内存注入）

**项目地址：**
- C++ DLL: https://github.com/shmocz/ra2yrcpp
- Python 客户端: https://github.com/shmocz/pyra2yr

**项目现状：**
- `ra2yrcpp`：539 commits，最新提交 2026-01-11，GPL-3.0 协议
- `pyra2yr`：11 commits，最新提交 2025-04-27，v0.3.0 发布于 2025-04-28
- 仍由 shmocz 一人维护，issue 较少响应
- 支持 Syringe + yrpp-spawner 方式注入（推荐），也支持 legacy spawner
- 提供 Docker 多游戏测试环境
- 支持 CnCNet YR client package 的游戏文件

**纯净版 YR 1.001 获取可行性：**
- ❌ 无合法公开下载渠道（EA 版权游戏）
- ⚠️ 可通过 CnCNet 社区客户端获取（需自有 CD Key 或使用社区安装包）
- ⚠️ ra2yrcpp 最新 README 提到推荐使用 CnCNet YR client package + Syringe + yrpp-spawner，而非要求完全纯净版
- ⚠️ 2026-01 更新了 "cncnet YR updates" 文档，说明已适配 CnCNet 版本
- ✅ Docker 环境可简化部署

**关键发现：** ra2yrcpp 最新版本已支持通过 Syringe + yrpp-spawner 与 CnCNet YR client 配合使用，不再严格要求"纯净版"。这可能绕过了我们之前的 Blocker。

**RL 适配性评估：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态可观测性 | ⭐⭐⭐⭐⭐ | Protobuf 结构化数据，全图信息，< 5ms 延迟 |
| 动作空间 | ⭐⭐⭐⭐ | 支持建造、移动、攻击等指令，但需自行封装 |
| Gymnasium 适配 | ⭐⭐ | pyra2yr 是异步 API，需大量封装工作 |
| 训练稳定性 | ⭐⭐ | 游戏崩溃风险高，需崩溃恢复机制 |
| 并行训练 | ⭐⭐ | 需多实例 Docker，每个实例需完整游戏 |
| 部署适配 | ⭐ | 训练环境与对战平台存在二进制差异 |

**优势：**
- 唯一能直接与原版 YR 游戏交互的方案
- 数据精度最高，延迟最低
- 与原版游戏行为 100% 一致

**劣势：**
- 需要游戏安装（版权灰色地带）
- 单人维护，上游依赖风险高
- 仅 Windows 可运行游戏进程
- 频繁崩溃需大量容错代码
- 不支持 headless 运行（必须渲染窗口）

---

### 方案 B：OpenRA-RL（⭐ 最推荐）

**项目地址：** https://github.com/yxc20089/OpenRA-RL

**项目现状：**
- 325 commits，最新提交 2026-04-22，GPL-3.0 协议
- **极其活跃**，2026 年 2 月至今几乎每周都有更新
- 已发布 pip 包：`pip install openra-rl`
- 版本号 v0.4.1
- 配套网站：https://openra-rl.dev/
- HuggingFace Space 在线演示
- 排行榜系统：https://huggingface.co/spaces/openra-rl/OpenRA-Bench

**核心架构：**
```
Agent ↔ FastAPI (port 8000) ↔ gRPC bridge (port 9999) ↔ OpenRA 游戏引擎 (C#)
```

**关键特性：**
- ✅ **完整的 Gymnasium 风格环境接口**（OpenEnv 标准）
- ✅ **Docker 一键部署**，headless 运行，无需 GPU 渲染
- ✅ **25Hz 游戏帧率**，独立于 Agent 速度
- ✅ **48 个游戏工具调用**（MCP 标准），支持 LLM Agent
- ✅ **64 局并发训练**（bench_multi_session.py）
- ✅ 支持 LLM Agent（Claude、GPT-4、Ollama 本地模型）
- ✅ 支持脚本 Bot、MCP Bot
- ✅ 回放系统（Docker 内 VNC 观看）
- ✅ 跨平台（macOS/Linux/Windows）
- ✅ AMD GPU 支持
- ✅ 中断机制（unit_arrived、production_complete 等事件驱动）

**观测空间：**
- tick、cash、ore、power_provided、power_drained
- 己方单位（位置、血量、类型、朝向、速度、攻击范围）
- 己方建筑（生产队列、电力、集结点）
- 可见敌方单位/建筑
- 完整的战争迷雾系统

**动作空间：**
- 48 个工具调用（MCP 标准），涵盖：
  - 读取类：地图分析、科技树查询、阵营简报
  - 移动类：单位移动、攻击移动、巡逻
  - 生产类：建造建筑、训练单位、生产队列管理
  - 战术类：集结点、编队、技能释放

**RL 适配性评估：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态可观测性 | ⭐⭐⭐⭐ | 结构化数据，但非原版引擎，部分细节有差异 |
| 动作空间 | ⭐⭐⭐⭐⭐ | 48 个工具调用，覆盖全面，MCP 标准化 |
| Gymnasium 适配 | ⭐⭐⭐⭐⭐ | OpenEnv 标准，pip install 即用 |
| 训练稳定性 | ⭐⭐⭐⭐ | C# 引擎稳定，headless 运行，崩溃少 |
| 并行训练 | ⭐⭐⭐⭐⭐ | 64 局并发，Docker 容器化 |
| 部署适配 | ⭐⭐⭐⭐ | Web 可访问，跨平台 |

**优势：**
- **开箱即用**，`pip install openra-rl` 即可开始
- 社区活跃，文档完善，持续迭代
- Docker headless 运行，适合规模化训练
- 已有 LLM Agent 和脚本 Bot 示例
- 跨平台，不依赖原版游戏安装
- 排行榜系统，可对比不同 Agent 表现

**劣势：**
- 基于 OpenRA 引擎（开源重制），**不是原版 YR**
- 部分游戏机制与原版有差异（如单位属性、AI 行为）
- 当前主要面向 LLM Agent，传统 RL（PPO 等）需自行适配
- OpenRA 的 RA2 mod 完成度约 80-90%，部分高级功能缺失
- GPL-3.0 协议限制商业使用

---

### 方案 C：Chrono Divide + ra2web-chronodivide-bot（Web 引擎）

**项目地址：**
- Chrono Divide: https://chronodivide.com/ （闭源游戏客户端）
- Bot 框架: https://github.com/ra2web/ra2web-chronodivide-bot
- Game API Playground: https://github.com/ra2web/game-api-playground
- RA2WEB 代理: https://github.com/ra2web/ra2web-proxy

**项目现状：**
- Chrono Divide：TypeScript 重写的 RA2 引擎，浏览器运行，功能基本完整
- ra2web-chronodivide-bot：43 stars，186 commits，TypeScript 实现
- RA2WEB（ra2web 组织）：211 followers，13 个仓库，国内社区活跃
- ra2web-proxy：98 stars，提供合规代理转发

**Bot API 特性：**
- 通过 WebSocket 连接游戏服务器
- 支持离线回放生成（`.rpl` 文件）
- 支持在线对战（人类 vs Bot）
- 需要本地 RA2 游戏文件（MIX 格式）作为资源
- Node 14 要求

**RL 适配性评估：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态可观测性 | ⭐⭐⭐ | API 提供基本状态，但不如内存注入精确 |
| 动作空间 | ⭐⭐⭐ | 支持建造、移动、攻击，但 API 有限 |
| Gymnasium 适配 | ⭐ | 无 Gymnasium 接口，TypeScript 生态，需大量桥接 |
| 训练稳定性 | ⭐⭐⭐ | Web 引擎相对稳定，但网络依赖 |
| 并行训练 | ⭐⭐ | 需多服务器实例，WebSocket 连接管理复杂 |
| 部署适配 | ⭐⭐⭐⭐⭐ | 浏览器运行，零安装，跨平台最佳 |

**优势：**
- 浏览器运行，零安装门槛
- 国内社区（RA2WEB）活跃，有中文文档
- 已有开源 AI Bot 实现
- 支持在线人机对战

**劣势：**
- **游戏客户端闭源**，API 由开发者控制
- TypeScript 生态，与 Python RL 框架（SB3、torch）需桥接
- 无 Gymnasium 接口，需从零封装
- 需要 RA2 原版 MIX 文件作为资源（版权问题）
- Bot API 功能有限，不如 ra2yrcpp 精确
- Node 14 版本限制
- 不支持 headless 训练（需浏览器环境）
- 主要面向规则 Bot，非 RL 训练设计

---

### 方案 D：OpenRA2/RA2Web（React 重构版）

**项目地址：** https://github.com/OpenRA2/RA2Web

**项目现状：**
- 87 commits，最新提交 2025-08-07
- 基于 Chrono Divide 客户端的反编译代码
- 使用 React 18 + TypeScript + Vite + Three.js 重构
- GPL-3.0 协议
- 仍处于早期开发阶段

**关键说明（来自项目 README）：**
> "这是基于 AI 对《时空分裂（chronodivide）》客户端的反编译，并意图基于最新的 React 和 Three 版本进行重构。但所有权利归《时空分裂（chronodivide）》的所有者所有。未经许可，严禁用于任何商业行为。"

**RL 适配性评估：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态可观测性 | ⭐⭐ | 反编译项目，API 不稳定 |
| 动作空间 | ⭐⭐ | 尚未形成标准接口 |
| Gymnasium 适配 | ⭐ | 无任何 RL 接口 |
| 训练稳定性 | ⭐ | 项目早期，不稳定 |
| 并行训练 | ⭐ | 不支持 |
| 部署适配 | ⭐⭐⭐ | Web 端，但成熟度不足 |

**优势：**
- React + Three.js 现代技术栈
- 社区驱动

**劣势：**
- **反编译项目，法律风险高**
- 项目极早期，功能不完整
- 无 RL 接口
- 不适合作为 RL 训练基础

**结论：❌ 不推荐。** 法律风险和技术成熟度均不足。

---

### 方案 E：OpenRA 官方 RA2 Mod

**项目地址：** https://github.com/OpenRA/ra2

**项目现状：**
- 1,162 commits，最新提交 2025-11-28
- OpenRA 官方 RA2 mod，C# 实现
- GPL-3.0 协议
- 社区维护，相对成熟
- 支持专用服务器（launch-dedicated.cmd/sh）
- 跨平台（Windows/macOS/Linux）

**RL 适配性评估：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态可观测性 | ⭐⭐⭐ | OpenRA 引擎可修改，但需 C# 开发 |
| 动作空间 | ⭐⭐⭐ | 引擎可扩展，但需自行实现 API |
| Gymnasium 适配 | ⭐⭐ | 无现成接口，但 OpenRA-RL 已做了这部分 |
| 训练稳定性 | ⭐⭐⭐⭐ | C# 引擎稳定，支持 headless |
| 并行训练 | ⭐⭐⭐ | 需自行实现多实例管理 |
| 部署适配 | ⭐⭐⭐⭐ | 跨平台，开源 |

**优势：**
- OpenRA 引擎成熟稳定
- 开源可修改
- 支持专用服务器模式
- 跨平台

**劣势：**
- **OpenRA-RL（方案 B）已在此基础上做了完整的 RL 封装**
- 直接使用此方案意味着要重复 OpenRA-RL 的工作
- RA2 mod 完成度约 80-90%
- C# 引擎修改需要 .NET 开发经验

**结论：** 如果选择 OpenRA 路线，应直接使用 OpenRA-RL（方案 B）而非从零开始。

---

### 方案 F：纯屏幕捕获方案（CV + CNN）

**说明：** 此方案不在用户提供的参考列表中，但作为备选记录。

**RL 适配性评估：**
| 维度 | 评分 | 说明 |
|------|------|------|
| 状态可观测性 | ⭐⭐ | 仅屏幕可见区域，受战争迷雾限制 |
| 动作空间 | ⭐⭐ | 鼠标/键盘模拟，精度低 |
| Gymnasium 适配 | ⭐⭐⭐ | 有成熟框架（如 gym-super-mario-bros） |
| 训练稳定性 | ⭐⭐ | 受分辨率、UI 缩放影响 |
| 并行训练 | ⭐⭐ | 需多虚拟显示器 |
| 部署适配 | ⭐⭐⭐⭐ | 适用于任何版本游戏 |

**结论：** 作为最后手段。延迟高、可观测性差、计算开销大，但兼容性最好。

---

## 三、综合对比

| 维度 | A: ra2yrcpp | B: OpenRA-RL | C: Chrono Divide | D: RA2Web | E: OpenRA RA2 |
|------|:-----------:|:------------:|:-----------------:|:---------:|:-------------:|
| 原版保真度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| 开箱即用 | ⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐ | ⭐⭐ |
| RL 适配 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐ |
| Gymnasium 接口 | ❌ 需自建 | ✅ OpenEnv | ❌ 需自建 | ❌ 无 | ❌ 需自建 |
| 并行训练 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐ | ⭐⭐⭐ |
| Headless 运行 | ❌ | ✅ Docker | ❌ 需浏览器 | ❌ 需浏览器 | ✅ |
| 跨平台 | ❌ Win only | ✅ | ✅ 浏览器 | ✅ 浏览器 | ✅ |
| 社区活跃度 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐ |
| 版权风险 | ⚠️ 灰色 | ✅ 开源 | ⚠️ 需 MIX | ❌ 反编译 | ✅ 开源 |
| LLM Agent 支持 | ❌ | ✅ | ⚠️ 有限 | ❌ | ❌ |
| 传统 RL 支持 | ⚠️ 需封装 | ⚠️ 需适配 | ❌ | ❌ | ⚠️ 需封装 |
| 部署到对战平台 | ⚠️ 有差异 | ❌ 不同引擎 | ❌ | ❌ | ❌ |

---

## 四、推荐方案

### 🏆 首选：方案 B — OpenRA-RL

**理由：**

1. **零阻塞启动**：`pip install openra-rl`，Docker 一键部署，无需原版游戏安装
2. **RL 生态最完善**：OpenEnv 标准接口、48 个 MCP 工具调用、64 局并发
3. **社区最活跃**：325 commits，2026 年持续迭代，有排行榜和在线演示
4. **训练基础设施完备**：headless 运行、回放系统、崩溃恢复
5. **可扩展性强**：支持 LLM Agent + 脚本 Bot + 传统 RL，多种 Agent 范式

**需要解决的问题：**
- OpenRA-RL 当前主要面向 LLM Agent（工具调用模式），需适配为传统 RL 的 `obs → action → reward` 循环
- OpenRA 引擎与原版 YR 的游戏机制差异（单位属性、AI 行为等）
- GPL-3.0 协议限制

### 🥈 备选：方案 A — ra2yrcpp + pyra2yr（重新评估）

**新发现：** ra2yrcpp 2026-01 更新已支持 CnCNet YR client package + Syringe + yrpp-spawner，可能不再需要"纯净版"安装。建议重新验证此路径。

**如果 OpenRA-RL 的游戏保真度不满足需求，可以：**
1. 先用 CnCNet 客户端 + Syringe + yrpp-spawner 尝试 ra2yrcpp 注入
2. 如果成功，则原方案可行
3. 如果失败，退回 OpenRA-RL

### ❌ 不推荐：方案 C/D

- 方案 C（Chrono Divide）：TypeScript 生态与 Python RL 框架不兼容，桥接成本高
- 方案 D（RA2Web）：反编译项目，法律风险，极早期

---

## 五、建议的新路线图

### Phase 0：双线验证（1-2 周）

**线路 A — OpenRA-RL 快速验证：**
- [ ] `pip install openra-rl` + Docker 部署
- [ ] 运行脚本 Bot 示例
- [ ] 评估观测空间/动作空间对 RL 训练的适配度
- [ ] 测试 headless 并行训练性能

**线路 B — ra2yrcpp 重新验证：**
- [ ] 安装 CnCNet YR client package
- [ ] 使用 Syringe + yrpp-spawner 注入 ra2yrcpp
- [ ] 运行 pyra2yr 连通性测试
- [ ] 对比原方案 Blocker 是否已解除

**Exit criteria：** 确定最终技术路线（OpenRA-RL 或 ra2yrcpp）。

### Phase 1：环境封装（2-3 周）

**如果选择 OpenRA-RL：**
- [ ] 基于 OpenRA-RL 的 OpenEnv 接口封装 Gymnasium 环境
- [ ] 实现传统 RL 的 `obs → action → reward` 循环（非 LLM 工具调用模式）
- [ ] 实现最小观测空间（标量特征）
- [ ] 实现最小动作空间（离散动作）
- [ ] 实现基础奖励函数
- [ ] 随机 Agent 压力测试

**如果选择 ra2yrcpp：**
- [ ] 按原路线图 Phase 1 执行

### Phase 2+：按原路线图推进

---

## 六、风险与缓解

| 风险 | 概率 | 缓解策略 |
|------|------|----------|
| OpenRA 引擎与原版差异过大 | 中 | Phase 0 双线验证，对比游戏行为 |
| OpenRA-RL 的 LLM 导向设计不适合传统 RL | 中 | 封装适配层，或直接使用 OpenEnv 底层 API |
| ra2yrcpp CnCNet 适配仍有问题 | 中 | 优先验证 OpenRA-RL 路线 |
| GPL-3.0 协议限制 | 低 | 项目本身开源，不影响研究用途 |
| OpenRA-RL 项目停止维护 | 低 | 325 commits + 活跃社区，风险可控；可 fork |

---

## 七、参考链接

| 项目 | 地址 | 协议 | 语言 |
|------|------|------|------|
| OpenRA-RL | https://github.com/yxc20089/OpenRA-RL | GPL-3.0 | Python/C# |
| ra2yrcpp | https://github.com/shmocz/ra2yrcpp | GPL-3.0 | C++ |
| pyra2yr | https://github.com/shmocz/pyra2yr | GPL-3.0 | Python |
| Chrono Divide | https://chronodivide.com/ | 闭源 | TypeScript |
| ra2web-chronodivide-bot | https://github.com/ra2web/ra2web-chronodivide-bot | - | TypeScript |
| RA2WEB | https://github.com/ra2web | - | TypeScript/JS |
| OpenRA2/RA2Web | https://github.com/OpenRA2/RA2Web | GPL-3.0 | TypeScript |
| OpenRA RA2 Mod | https://github.com/OpenRA/ra2 | GPL-3.0 | C# |
| OpenRA-RL 官网 | https://openra-rl.dev/ | - | - |
| OpenRA-RL 排行榜 | https://huggingface.co/spaces/openra-rl/OpenRA-Bench | - | - |

---

## 八、验证进展与问题记录（2026-05-18）

### 8.1 已完成的验证工作

| 任务 | 状态 | 详情 |
|------|------|------|
| 创建 Python 虚拟环境 | ✅ 完成 | `<conda_env_path>`，Python 3.10.18 |
| 调研文档整理 | ✅ 完成 | 本报告已整理 6 种技术方案对比 |
| 路线图更新 | ✅ 完成 | 更新为双线验证路线 |

### 8.2 当前阻塞问题

#### 问题 1：OpenRA-RL 安装失败
- **现象：** `pip install openra-rl` 安装到最后阶段失败
- **错误信息：** `OSError: [WinError 5] 拒绝访问。: '<conda_env_path>\\Lib\\site-packages\\openra_env'`
- **可能原因：** 文件权限问题，或后台进程锁定了目标文件
- **影响：** 线路 A 验证无法继续
- **建议解决方案：**
  1. 删除现有虚拟环境，重新创建
  2. 尝试使用系统已有的环境（如 `lerobot` 或 `egp`）
  3. 以管理员权限运行安装命令
  4. 手动下载安装包并解压

#### 问题 2：Git 不在系统 PATH
- **现象：** 终端中执行 `git --version` 报错 "git 不是内部或外部命令"
- **影响：** 无法执行 `git push` 同步代码到远程仓库
- **建议解决方案：**
  1. 安装 Git for Windows（如果尚未安装）
  2. 将 Git 安装目录添加到系统 PATH
  3. 使用 Git Bash 或其他终端执行 git 命令

### 8.3 待执行的验证步骤

#### 线路 A — OpenRA-RL
- [ ] 解决安装权限问题后，重新执行 `pip install openra-rl`
- [ ] 运行脚本 Bot 示例验证环境连通性
- [ ] 评估观测空间/动作空间对 RL 训练的适配度
- [ ] 测试 headless 并行训练性能

#### 线路 B — ra2yrcpp
- [ ] 安装 CnCNet YR client package
- [ ] 下载 ra2yrcpp 预编译 DLL 和 Syringe
- [ ] 使用 Syringe + yrpp-spawner 注入 ra2yrcpp
- [ ] 运行 pyra2yr 连通性测试
- [ ] 验证原方案 Blocker 是否已解除

### 8.4 下一步行动建议

1. **优先解决 OpenRA-RL 安装问题**（线路 A）：尝试以管理员权限重新安装，或使用其他虚拟环境
2. **并行准备线路 B 验证**：下载 CnCNet YR client 和 ra2yrcpp 工具
3. **配置 Git 环境**：确保代码可同步到远程仓库

### 8.5 文档版本记录

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2026-05-18 | 初始版本，完成 6 种技术方案调研 |
| v1.1 | 2026-05-18 | 添加验证进展与问题记录章节 |
