<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1b27,50:0d1117,100:161b22&height=120&section=header&fontSize=0" width="100%"/>

# 📦 TG-Radar Plugins

<a href="https://git.io/typing-svg"><img src="https://readme-typing-svg.demolab.com?font=JetBrains+Mono&weight=600&size=16&duration=3000&pause=1000&color=3FB950&center=true&vCenter=true&repeat=true&width=380&height=28&lines=Official+Plugin+Repository" alt="Typing SVG" /></a>

<br/>

[![Plugins](https://img.shields.io/badge/7-3fb950?style=flat-square&label=plugins)]()&nbsp;
[![SDK](https://img.shields.io/badge/PluginContext-58a6ff?style=flat-square&label=SDK)]()&nbsp;
[![Hot Reload](https://img.shields.io/badge/✓-3fb950?style=flat-square&label=hot%20reload)]()&nbsp;
[![Auto Fuse](https://img.shields.io/badge/✓-3fb950?style=flat-square&label=auto%20fuse)]()

<br/>

[🏠 **核心仓库 →**](https://github.com/chenmo8848/TG-Radar) · [**快速开发**](#-快速开发) · [**SDK 接口**](#-sdk-接口) · [**插件管理**](#-插件管理)

</div>

---

## 📋 插件列表

### Admin 插件

| 插件 | 命令 | 配置 | 说明 |
|:--|:--|:--|:--|
| **general** | `ping` `status` `version` `config` `log` `jobs` | `panel_auto_delete_seconds` `recycle_command_seconds` | 通用面板 |
| **folders** | `folders` `rules` `enable` `disable` | — | 分组管理 |
| **rules** | `addrule` `setrule` `delrule` `setnotify` `setalert` `setprefix` | — | 规则维护 |
| **routes** | `routes` `addroute` `delroute` `sync` `routescan` | `auto_sync_enabled/time` `auto_route_enabled/time` | 自动归纳 |
| **system** | `restart` `update` | `restart_delay_seconds` | 系统任务 |
| **chatinfo** | *(转发自动触发)* | — | 群 ID 识别 · 实时同步 |

### Core 插件

| 插件 | 配置 | 说明 |
|:--|:--|:--|
| **keyword_monitor** | `bot_filter` `max_preview_length` | 关键词匹配与告警 |

---

## 🚀 快速开发

保存到 `plugins/admin/hello.py`，发送 `-reload hello` 即刻生效：

```python
PLUGIN_META = {"name": "hello", "version": "1.0.0", "kind": "admin"}
from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    @ctx.command("hello", summary="打招呼", usage="hello", category="示例")
    async def _(app, event, args):
        await ctx.reply(event, ctx.ui.panel("Hello", [ctx.ui.section("", ["👋"])]))
```

<details>
<summary>📄 <b>完整模板</b></summary>

```python
PLUGIN_META = {
    "name": "my_plugin", "version": "1.0.0", "description": "说明",
    "kind": "admin",
    "config_schema": {"my_key": {"type": "int", "default": 10, "description": "配置说明"}},
}
from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    ui, log = ctx.ui, ctx.log

    @ctx.command("mycommand", summary="做某事", usage="mycommand [参数]", category="分类")
    async def handler(app, event, args):
        value = ctx.config.get("my_key")
        log.info("执行, args=%s", args)
        await ctx.reply(event, ui.panel("结果", [
            ui.section("输出", [ui.bullet("参数", args), ui.bullet("配置", value)])]))

    @ctx.on("rule_changed")
    async def on_event(data): log.info("事件: %s", data)

    @ctx.healthcheck
    async def check(app): return "ok", "正常"

    @ctx.cleanup
    async def clean(): log.info("清理完成")
```
</details>

---

## 📚 SDK 接口

| 分类 | 接口 | 说明 |
|:--|:--|:--|
| 配置 | `ctx.config.get / set / all` | 读写插件配置（`configs/name.json`） |
| 数据 | `ctx.db.list_folders / get_rules / log_event` | 白名单 DB |
| 渲染 | `ctx.ui.panel / section / bullet / escape` | HTML 渲染 |
| 任务 | `ctx.bus.submit_job(kind, ...)` | 后台任务 |
| 日志 | `ctx.log` | 插件独立日志 |
| 事件 | `ctx.emit` / `@ctx.on` | 事件总线 |
| 注册 | `@ctx.command` / `@ctx.hook` / `@ctx.cleanup` / `@ctx.healthcheck` | 装饰器 |
| 工具 | `ctx.client` / `ctx.reply` | Telethon / 回复 |

---

## 🔧 插件管理

| 命令 | 说明 |
|:--|:--|
| `-plugins` | 全部状态 |
| `-reload name` | 热重载 |
| `-pluginreload` | 全量重载 |
| `-pluginenable / -plugindisable name` | 启用 / 停用 |
| `-pluginconfig name [key] [val]` | 配置管理 |
| `-update` | 拉取更新 + 自动重载 |

---

## 📂 插件配置

声明了 `config_schema` 的插件自动生成配置文件，也可直接编辑后 `-reload`：

```
configs/
├── general.json           {"panel_auto_delete_seconds": 45, "recycle_command_seconds": 8}
├── routes.json            {"auto_sync_enabled": true, "auto_sync_time": "03:40", ...}
├── keyword_monitor.json   {"bot_filter": true, "max_preview_length": 760}
└── system.json            {"restart_delay_seconds": 2.0}
```

---

## ♻️ 生命周期

```
  ┌──────┐   setup() 成功   ┌────────┐   连续失败 N 次   ┌──────┐
  │ 发现  │ ───────────────→ │ 运行中  │ ────────────────→ │ 熔断  │
  └──────┘                  └────────┘                   └──────┘
      │                        ↑    │                       │
      │ 异常                   │    │ -plugindisable        │ -reload
      ↓                       │    ↓                       │
  ┌────────┐  修复+-reload    │  ┌──────┐  -pluginenable   │
  │ 加载失败 │ ───────────────┘  │ 已停用 │ ────────────────┘
  └────────┘                    └──────┘
```

---

## ⚠️ 免责声明

本项目仅供**学习与技术研究**用途。严禁用于非法活动。使用即表示同意。

---

<div align="center">

[**Core**](https://github.com/chenmo8848/TG-Radar) · [**Plugins**](https://github.com/chenmo8848/TG-Radar-Plugins)

<sub>Built with Telethon · SQLite WAL · APScheduler</sub>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1a1b27,50:0d1117,100:161b22&height=80&section=footer&fontSize=0" width="100%"/>

</div>
