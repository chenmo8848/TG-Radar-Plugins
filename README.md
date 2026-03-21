# TG-Radar-Plugins

TG-Radar 的外部插件仓库。

## 目录结构

- `plugins/admin/`：Admin 命令插件
- `plugins/core/`：Core 运行时插件

## 默认安装位置

```text
/root/TG-Radar/plugins-external/TG-Radar-Plugins
```

核心仓库默认会从这里加载外部插件，不需要你手工做软链接。

## 当前包含的插件

### Admin
- `general.py`：帮助、状态、作业、日志等轻命令
- `folders.py`：分组管理
- `rules.py`：规则管理
- `routes.py`：自动归纳 / 路由相关命令
- `system.py`：系统与更新相关命令

### Core
- `keyword_monitor.py`：关键词监控主插件

## 说明

这套插件仓库设计目标是：

- 修某个功能时只改对应插件文件
- 不因为单个插件出问题而去改整套核心仓库
- 配合核心的命令注册中心，让 `-help` 自动按已注册插件生成
