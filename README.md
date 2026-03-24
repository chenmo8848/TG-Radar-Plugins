<div align="center">

<img src="docs/banner.svg" alt="TG-Radar Plugins Banner" width="100%" style="max-width: 800px; margin-bottom: 20px;" />

# 📦 TG-Radar Plugins

**TG-Radar 官方扩展生态与沙盒插件注册中心**

[![Plugins](https://img.shields.io/badge/Official_Plugins-5+-3FB950?style=for-the-badge&logo=codeigniter&logoColor=white)](#-内置组件概览)
[![SDK](https://img.shields.io/badge/PluginContext_SDK-Ready-2EA043?style=for-the-badge&logo=python&logoColor=white)](#-sdk-架构赋能)
[![Hot Reload](https://img.shields.io/badge/Hot_Reload-Supported-000000?style=for-the-badge&logo=quicktime&logoColor=white)](#)

[**🏠 核心基座**](https://github.com/x72dev/TG-Radar) • [**📦 组件概览**](#-内置组件概览) • [**🚀 快速开发**](#-极速开发实践) • [**📚 SDK 架构**](#-sdk-架构赋能)

</div>

---

## 📖 生态简介

此仓库为 `TG-Radar` 架构的专属扩展池。为了保证核心基座的极致轻量与稳定性，TG-Radar 将所有的上层业务逻辑（包括面板渲染、命令解析、自动化路由、甚至关键词监控引擎）全部剥离至此。

通过严苛的生命周期管控与沙盒化的 `PluginContext` SDK，插件在主引擎的高频异步事件循环中运行，却享受着 **完全隔离的错误熔断** 与 **毫秒级热重载（Hot-Reload）** 特权。

---

## 📦 内置组件概览

生态池内的组件按职责严格划分为负责后台调度的 **Admin 层** 与负责高频监听拦截的 **Core 层**。

| 模块名 | 类型 | 核心职责 | 依赖特性 |
| :--- | :--- | :--- | :--- |
| `keyword_monitor` | **Core** | **核心引警**：承担海量并发下的关键词高精度正则匹配与告警格式化抛出。 | `Telethon Events`, `Asyncio` |
| `general` | Admin | 基础系统监控：提供 Ping 延时测试、系统大盘状态展示与日志穿透分发。 | `System Metrics`, `SQLite` |
| `folders` | Admin | 分组网格管控：实现监控群组对象的动态生命周期管理（实时启停与销毁）。 | `Database Sync` |
| `rules` | Admin | 正则规则栈：维护基于预编译正则表达式的高性能捕获规则队列。 | `Regex Engine` |
| `routes` | Admin | 流量调度：负责数据的智能自动归纳与流量分发。 | `Scheduler Tasks` |
| `chatinfo` | Admin | 来源识别：监听收藏夹的转发消息，极速逆向解析群组来源 ID 与属性。 | `Message Forwarding` |

---

## 🚀 极速开发实践

得益于 TG-Radar 的强解耦架构，您只需寥寥数行代码即可创造一个具备完整生命周期、并原生支持热重载的强大扩展：

**1. 创建插件脚本** (`plugins/admin/hello.py`)：
```python
# 声明插件元数据，系统将自动据此进行挂载
PLUGIN_META = {"name": "hello", "version": "1.0.0", "kind": "admin"}

from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    
    # 注册一个自定义命令
    @ctx.command("hello", summary="打招呼测试", usage="hello", category="示例模块")
    async def handler(app, event, args):
        
        # 使用内置的 UI 渲染器输出标准化的高级面板
        panel_html = ctx.ui.panel("Hello World", [
            ctx.ui.section("状态", ["👋 您的第一个热重载插件已成功运行！"])
        ])
        await ctx.reply(event, panel_html)
```

**2. 极速热装载**：
在 TG 收藏夹发送 `-reload hello`，引擎将瞬间将该代码编译并加载进内存上下文，立即生效！

---

## 📚 SDK 架构赋能

`PluginContext` 暴露了沙盒内的高权限安全接口，完美屏蔽了底层的长链接通信细节。

### 核心能力矩阵

- **⚙️ 配置隔离 (`ctx.config`)**
  自动为您生成独立的 `configs/插件名.json`。支持强类型验证与默认值注入。
  *调用：`ctx.config.get("api_key")`*

- **🗄️ 状态持久化 (`ctx.db`)**
  不要在全局作用域缓存关键数据（热重载会将其清空）。使用 DB 接口实现状态穿透与安全持久化。
  *调用：`ctx.db.log_event("INFO", ...)`*

- **🎨 UI 渲染器 (`ctx.ui`)**
  无需手拼繁杂的 HTML 标签，SDK 提供了企业级的 UI 渲染链，确保所有插件的输出排版具有高度一致的美感。
  *调用：`ctx.ui.panel(title, sections)`*

- **⏱️ 异步调度总线 (`ctx.bus`)**
  **严禁在 handler 中执行阻塞型 I/O！** 对于网络请求或密集运算，请将其甩入后台事件总线。
  *调用：`ctx.bus.submit_job("kind", func, *args)`*

- **🔗 核心钩子 (`@ctx.hook`)**
  允许高级插件将自身逻辑横向切入 Core 引擎的特定生命周期节点（如消息触达瞬间、规则命中时刻）。

---

## 🛠️ 最佳实践与避坑

> [!WARNING]
> **永远不要阻塞事件循环**
> 整个架构基于 `asyncio` 驱动，如果在插件中使用 `time.sleep()` 或同步的 `requests.get()`，将导致整个 Telegram 机器人的监听陷入卡死！请务必使用 `aiohttp` 或 `asyncio.sleep()`。

> [!TIP]
> **配置文件热生效**
> 修改 `configs/*.json` 后，您不需要重启容器。直接发送 `-reload [插件名]`，最新的配置项将被立即反序列化并注入运行实例中。
