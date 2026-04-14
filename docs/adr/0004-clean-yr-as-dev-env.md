# ADR-0004: 开发环境使用纯净版 YR 1.001

## Status

Accepted

## Context

`ra2yrcpp` 的底层库 YRpp 中包含大量硬编码信息：

- 游戏内部类（`TechnoClass`、`HouseClass`、`BuildingClass` 等）的字段偏移
- 游戏函数的绝对内存地址
- 游戏主循环的 Hook 点

这些信息来源于对纯净版 YR 1.001 `gamemd.exe` 的逆向工程。任何修改 `gamemd.exe` 或其加载流程的补丁都会破坏这些假设。

社区补丁 Ares 和 Phobos 会：

- 扩展核心类结构，添加新字段，导致已有字段偏移错位
- 在 `ra2yrcpp` 预期的位置注入自己的 Hook
- 修改某些游戏函数的签名与行为

向打了 Ares/Phobos 的 `gamemd.exe` 注入 `ra2yrcpp.dll` 会产生 Hook 冲突与数据错位，结果是崩溃或读取到无效数据。

本项目面向的中国对战平台版本（如红警战网）同样内置了平台特有补丁（联机同步、反作弊），与纯净版二进制不同。

## Decision

**开发环境：** 使用干净的 YR 1.001 安装，目录仅包含官方原版文件 + `ra2yrcpp.dll` + `Syringe.exe`，不得包含任何社区补丁（Ares、Phobos、CnCNet spawner 等）。

**部署环境差异：** 训练环境与对战平台的二进制差异问题延后到 Phase 5 处理。

**游戏文件处置：** 游戏文件不提交到 Git（版权 + 体积），通过 `.gitignore` 排除。

## Consequences

**收益：**
- 保证 `ra2yrcpp` 能稳定工作
- 避免多 Hook 冲突带来的难以定位的崩溃

**代价：**
- 需要单独维护纯净版安装，与日常游玩的平台版隔离
- 训练好的模型不能直接在对战平台使用（需 Phase 5 解决）

**不做：**
- 不尝试让 `ra2yrcpp` 兼容 Ares/Phobos 版本（维护成本远超收益）
- 不把游戏文件纳入代码仓库
