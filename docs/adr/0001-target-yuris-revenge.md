# ADR-0001: 目标游戏选择 Yuri's Revenge

## Status

Accepted

## Context

项目最初设定为针对《红色警戒2》原版 (`game.exe`) 开发 AI。然而核心依赖 `ra2yrcpp` 及其底层的 YRpp 库是围绕《尤里的复仇》(Yuri's Revenge, YR) 的 `gamemd.exe` 构建的：

- YRpp 的类定义、函数地址、Hook 点均基于 YR 1.001 二进制
- RA2 原版的内存布局与 YR 存在差异，无法直接复用
- 社区生态（Ares、Phobos、CnCNet）也以 YR 为中心

同时，中国主流对战平台（红警战网、兰博玩等）普遍使用 YR 作为对战版本。

## Decision

以 **Yuri's Revenge (gamemd.exe)** 作为目标游戏，而非 RA2 原版。

## Consequences

**收益：**
- 直接使用现成的 `ra2yrcpp` + YRpp，无需自行逆向 RA2 原版二进制
- 与中国对战平台的部署目标一致
- 游戏内容上，YR 是 RA2 的超集，包含 RA2 全部阵营和单位

**代价：**
- Agent 学到的策略包含对尤里阵营的处理（RA2 原版没有此阵营）
- 若将来需要支持 RA2 原版，需要额外的适配工作
