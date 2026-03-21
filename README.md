<div align="center">

# TG-Radar Plugins

**全解耦插件仓库**

每个插件独立运行 · 热重载 · 独立配置 · 独立日志

</div>

---

## 插件列表

### Admin 插件

| 插件 | 命令 | 配置 | 说明 |
|:-----|:-----|:-----|:-----|
| **general** | ping status version config log jobs | `panel_auto_delete_seconds` `recycle_command_seconds` | 通用面板 |
| **folders** | folders rules enable disable | — | 分组管理 |
| **rules** | addrule setrule delrule setnotify setalert setprefix | — | 规则维护 |
| **routes** | routes addroute delroute sync routescan | `auto_sync_enabled` `auto_sync_time` `auto_route_enabled` `auto_route_time` | 自动归纳 |
| **system** | restart update | `restart_delay_seconds` | 系统任务 |
| **chatinfo** | *(转发自动触发)* | — | 群 ID 识别 · 分组变动实时同步 |

### Core 插件

| 插件 | 配置 | 说明 |
|:-----|:-----|:-----|
| **keyword_monitor** | `bot_filter` `max_preview_length` | 关键词监控与告警 |

---

## 开发新插件

```
1. 复制 plugin_template.py → plugins/admin/my_plugin.py
2. 填写 PLUGIN_META
3. 实现 setup(ctx: PluginContext)
4. 发送 -reload my_plugin 热加载
```

### 最小示例

```python
PLUGIN_META = {"name": "hello", "version": "1.0.0", "kind": "admin"}
from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    @ctx.command("hello", summary="打招呼", usage="hello", category="示例")
    async def _(app, event, args):
        await ctx.reply(event, ctx.ui.panel("Hello", [ctx.ui.section("", ["👋"])]))
```

### SDK 接口

```python
from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    ctx.config.get(key)           # 读插件配置 (configs/name.json)
    ctx.config.set(key, val)      # 写配置 (自动持久化)
    ctx.db.list_folders()         # 白名单数据库方法
    ctx.ui.panel(title, [...])    # HTML 渲染
    ctx.bus.submit_job(kind, ...) # 提交后台任务
    ctx.log.info("...")           # 插件独立日志
    ctx.client                    # Telethon client
    ctx.emit(event, data)         # 发布事件
    ctx.reply(event, text)        # 统一回复

    @ctx.command(name, ...)       # 注册命令
    @ctx.hook(name, ...)          # 注册消息钩子
    @ctx.on(event_name)           # 订阅事件
    @ctx.cleanup                  # 卸载清理
    @ctx.healthcheck              # 健康检查
```

---

## 插件管理

| 命令 | 功能 |
|:-----|:-----|
| `-plugins` | 查看所有插件状态 |
| `-reload name` | 热重载单个插件 |
| `-pluginreload` | 全量重载 |
| `-pluginenable name` | 启用 |
| `-plugindisable name` | 停用（持久化） |
| `-pluginconfig name [k] [v]` | 查看/修改配置 |

## 插件配置

每个插件的配置自动生成在 `configs/` 目录：

```
configs/
├── general.json           {"panel_auto_delete_seconds": 45, ...}
├── routes.json            {"auto_sync_enabled": true, "auto_sync_time": "03:40", ...}
├── keyword_monitor.json   {"bot_filter": true, "max_preview_length": 760}
└── system.json            {"restart_delay_seconds": 2.0}
```

---

## 生命周期

```
发现 → 加载 → 运行中 ←→ 停用
                ↓
         连续失败 N 次
                ↓
             熔断 → reload → 运行中
```
