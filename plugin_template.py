"""
TG-Radar 插件模板 — 复制此文件到 plugins/admin/ 或 plugins/core/ 即可开发新插件。
唯一入口: from tgr.plugin_sdk import PluginContext
配置文件自动生成: configs/插件名.json
"""

PLUGIN_META = {
    "name": "my_plugin",
    "version": "1.0.0",
    "description": "插件说明",
    "author": "your_name",
    "kind": "admin",
    "depends": [],
    "conflicts": [],
    "min_core_version": "6.0.0",
    "config_schema": {
        "example_key": {"type": "int", "default": 10, "description": "示例配置"},
    },
}

from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    ui, log = ctx.ui, ctx.log

    @ctx.command("mycommand", summary="示例命令", usage="mycommand [参数]", category="示例")
    async def handler(app, event, args):
        value = ctx.config.get("example_key")
        log.info("mycommand args=%s config=%s", args, value)
        await ctx.reply(event, ui.panel("TG-Radar · 示例", [ui.section("结果", [ui.bullet("参数", args or "无"), ui.bullet("配置", value)])]), prefer_edit=False)

    @ctx.on("rule_changed")
    async def on_rule(data):
        log.info("规则变更: %s", data)

    @ctx.healthcheck
    async def check(app):
        return "ok", "正常"

    @ctx.cleanup
    async def clean():
        log.info("卸载清理完成")

def teardown(ctx: PluginContext):
    pass
