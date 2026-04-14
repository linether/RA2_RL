# Technical Notes

记录项目实施中需要注意的技术约束与已知限制。

---

## 开发环境要求：纯净版 YR 1.001

`ra2yrcpp` 依赖的 YRpp 库是针对纯净版 YR 1.001 `gamemd.exe` 二进制布局的逆向工程结果。YRpp 中的类偏移、vtable 位置、函数绝对地址全部硬编码。

打了 Ares、Phobos 等社区补丁的 `gamemd.exe` 会：
- 扩展 `TechnoClass`、`HouseClass` 等核心类，导致字段偏移错位
- 在 `ra2yrcpp` 试图 hook 的位置注入自己的 hook，产生冲突
- 修改函数签名，调用时参数错位

**实际影响：** 向打了补丁的 `gamemd.exe` 注入 `ra2yrcpp.dll` 会导致崩溃或读取到无效数据。

**开发环境约定：**
- 开发目录使用纯净版 YR 1.001 安装，目录中不得包含 `Ares.dll`、`Phobos.dll`、`gamemd-ares.exe`、`gamemd-spawn.exe` 等社区补丁产物
- 仅官方原版文件 + `ra2yrcpp.dll` + `Syringe.exe`
- 不提交游戏文件到 Git

---

## pyra2yr API 特性

`pyra2yr` 提供的是**异步客户端 API**，不是 Gymnasium 接口：

- `ExManager` — 连接与注入管理
- `Game` — 游戏会话
- `state.query_objects()` — 状态查询

Gymnasium 的 `reset()` / `step()` 同步接口需要在 `RA2Env` 中自行封装，包括：
- 异步 API 到同步调用的适配
- 观测空间的序列化到 NumPy 数组
- 动作空间的反序列化到 pyra2yr 指令
- Episode 终止判定与重启

---

## 回放数据限制

YR 的原生回放格式记录的是输入事件序列（用于确定性重放），不直接包含每帧游戏状态。从回放提取 `(state, action)` 训练对需要额外构建 pipeline：在回放模式下用 `ra2yrcpp` 记录每帧状态，并与输入序列对齐。

初期路线图不依赖回放数据。

---

## 部署环境差异

中国对战平台（红警战网等）的 `gamemd.exe` 也打了平台自有的补丁（联机同步、反作弊等），内存布局与纯净版不同。

这意味着训练环境（纯净版）和部署环境（平台版）之间存在 gap。处理方案延后到 Phase 5，可能路径：
- 为平台版重新定位 hook 地址
- 训练后期切换到屏幕捕获方案进行部署适配
- 若平台版恰好兼容 `ra2yrcpp`，则直接复用

---

## 上游依赖维护状态

- `shmocz/ra2yrcpp` 与 `shmocz/pyra2yr` 均为单人维护
- 存在已报告的连接稳定性与日志相关 issue
- 应尽早 fork，备份 Proto 定义文件，遇 bug 时本地修复
