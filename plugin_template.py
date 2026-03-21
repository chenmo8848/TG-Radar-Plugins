"""
TG-Radar 插件模板
=================

复制此文件到 plugins/admin/ 或 plugins/core/ 目录，按需修改。

文件名即插件名（不含 .py），例如 my_plugin.py → 插件名为 my_plugin。

Admin 插件：注册命令（register_command），在 Telegram 收藏夹通过命令触发。
Core 插件：注册消息钩子（register_message_hook），监听所有群消息并处理。

生命周期：
    setup(ctx)       → 插件加载时调用，注册命令/钩子/健康检查/清理函数
    teardown(ctx)     → 插件卸载时调用（可选），用于清理资源
    healthcheck(app)  → 健康检查（可选），返回 (status, detail) 或字符串
"""

# ---- 元数据声明 ----
PLUGIN_META = {
    "name": "my_plugin",               # 插件名，建议与文件名一致
    "version": "1.0.0",                 # 语义化版本
    "description": "插件功能简述",       # 简短说明
    "author": "your_name",              # 作者
    "kind": "admin",                    # "admin" 或 "core"
    "depends": [],                       # 依赖的其他插件名列表
    "conflicts": [],                     # 冲突的插件名列表
    "min_core_version": "6.0.0",        # 最低核心版本要求
    "config_schema": {                   # 可配置项（通过 pluginconfig 命令读写）
        "example_key": {
            "type": "bool",
            "default": True,
            "description": "示例配置项",
        },
    },
}

# ---- 导入 ----
# 只从 tgr.telegram_utils 导入渲染工具，保持解耦
from tgr.telegram_utils import bullet, escape, panel, section


# ---- Admin 插件：命令处理函数 ----

async def cmd_example(app, event, args):
    """
    命令处理函数签名：async def handler(app, event, args)
        app   - AdminApp 实例，可访问 app.db / app.config / app.safe_reply 等
        event - Telethon NewMessage.Event
        args  - 命令后的参数字符串（已去除前缀和命令名）
    """
    # 读取插件自有配置
    # cfg_value = ctx 在 setup 中保存的引用...
    # 或者直接通过 app.db.get_plugin_config("my_plugin") 读取

    await app.safe_reply(
        event,
        panel("TR 管理器 · 示例命令", [
            section("执行结果", [
                bullet("参数", args or "无"),
                bullet("状态", "正常"),
            ]),
        ]),
        prefer_edit=False,
    )


# ---- Core 插件：消息钩子函数 ----
# （如果 kind 是 "core"，则注册 message_hook 而非 command）

# async def message_hook(app, event):
#     """
#     消息钩子签名：async def handler(app, event)
#         app   - CoreApp 实例
#         event - Telethon NewMessage.Event
#     """
#     pass


# ---- 健康检查（可选）----

async def healthcheck(app):
    """
    返回格式：
        (status, detail) - status 为 "ok" / "warn" / "error"
        或直接返回字符串（status 默认为 "ok"）
    """
    return "ok", "插件运行正常"


# ---- 清理函数（可选）----

async def my_cleanup():
    """卸载时需要执行的清理逻辑，例如关闭连接、取消定时器等。"""
    pass


# ---- 入口：setup ----

def setup(ctx):
    """
    ctx 是 PluginContext 实例，提供以下方法：

    ctx.register_command(name, handler, *, summary, usage, category, aliases, heavy, hidden)
    ctx.register_message_hook(name, handler, *, summary, order)
    ctx.register_cleanup(func)          # 卸载时调用
    ctx.set_healthcheck(func)           # 健康检查
    ctx.get_config(key, default=None)   # 读取插件配置

    ctx.app      - AdminApp / CoreApp 引用
    ctx.plugin   - 当前 PluginRecord
    """
    # Admin 命令注册
    ctx.register_command(
        "example",
        cmd_example,
        summary="示例命令",
        usage="example [参数]",
        category="示例分类",
        heavy=False,        # True = 进入后台排队执行
        hidden=False,       # True = 不出现在 help 列表
    )

    # 健康检查
    ctx.set_healthcheck(healthcheck)

    # 清理函数（插件卸载/重载时调用）
    ctx.register_cleanup(my_cleanup)


# ---- 卸载入口（可选）----

async def teardown(ctx):
    """插件被卸载时调用，在所有 cleanup 函数之后执行。"""
    pass
