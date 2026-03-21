# TG-Radar-Plugins v6.0.0

TG-Radar 插件仓库，采用全解耦插件化架构。

## 插件列表

### Admin 插件（命令交互）

| 插件 | 说明 | 命令 |
|------|------|------|
| `general` | 通用面板与日志 | `ping` `status` `version` `config` `log` `jobs` |
| `folders` | 分组查看与启停 | `folders` `rules` `enable` `disable` |
| `rules` | 规则维护与通知 | `addrule` `setrule` `delrule` `setnotify` `setalert` `setprefix` |
| `routes` | 自动归纳与同步 | `routes` `addroute` `delroute` `sync` `routescan` |
| `system` | 系统重启与更新 | `restart` `update` |

### Core 插件（消息处理）

| 插件 | 说明 |
|------|------|
| `keyword_monitor` | 关键词监控与告警发送 |

## 开发新插件

1. 复制 `plugin_template.py` 到 `plugins/admin/` 或 `plugins/core/`
2. 填写 `PLUGIN_META` 元数据
3. 实现 `setup(ctx)` 注册命令或钩子
4. 实现 `teardown(ctx)` 做清理（可选）
5. 在 Telegram 发送 `-reload 插件名` 热加载

## 插件管理命令

```
-plugins              查看所有插件状态
-pluginreload         全量重载所有插件
-reload <名称>        重载单个插件
-pluginenable <名称>  启用已停用的插件
-plugindisable <名称> 停用插件（重启保持停用）
-pluginconfig <名称>  查看/修改插件配置
```

## 插件生命周期

```
[发现] → load → [已加载] → enable → [运行中]
                                       ↓
                               连续失败 N 次
                                       ↓
                                    [已熔断] → fix+reload → [运行中]
                                       ↓
                                   disable
                                       ↓
                                    [已停用] ← plugindisable
```

## PLUGIN_META 完整字段

```python
PLUGIN_META = {
    "name": "my_plugin",           # 插件名
    "version": "1.0.0",            # 版本号
    "description": "功能说明",      # 描述
    "author": "作者",               # 作者
    "kind": "admin",               # admin 或 core
    "depends": [],                  # 依赖插件列表
    "conflicts": [],                # 冲突插件列表
    "min_core_version": "6.0.0",   # 最低核心版本
    "config_schema": {              # 可配置项
        "key": {"type": "bool", "default": True, "description": "说明"},
    },
}
```
