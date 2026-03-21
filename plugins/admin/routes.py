"""自动归纳与同步。"""

PLUGIN_META = {
    "name": "routes",
    "version": "6.0.0",
    "description": "自动归纳与同步",
    "kind": "admin",
    "config_schema": {
        "auto_sync_enabled": {"type": "bool", "default": True, "description": "启用每日自动同步"},
        "auto_sync_time": {"type": "str", "default": "03:40", "description": "自动同步时间 HH:MM"},
        "auto_route_enabled": {"type": "bool", "default": True, "description": "启用每日自动归纳"},
        "auto_route_time": {"type": "str", "default": "04:20", "description": "自动归纳时间 HH:MM"},
    },
}

import shlex
from tgr.plugin_sdk import PluginContext, normalize_pattern_from_terms


def _shlex(args: str) -> list[str]:
    try:
        return shlex.split(args) if args else []
    except ValueError:
        return args.split()


def setup(ctx: PluginContext):
    ui = ctx.ui

    @ctx.command("routes", summary="查看自动归纳规则", usage="routes", category="自动归纳")
    async def cmd_routes(app, event, args):
        rows = ctx.db.list_routes()
        if not rows:
            await ctx.reply(event, ui.panel("TG-Radar · 归纳规则", [ui.section("状态", ["· <i>暂无规则</i>"])]), prefer_edit=False)
            return
        blocks = [f"<b>{ui.escape(r['folder_name'])}</b>\n· <code>{ui.escape(r['pattern'])}</code>" for r in rows]
        await ctx.reply(event, ui.panel("TG-Radar · 归纳规则", [ui.section("当前", blocks)]), auto_delete=75, prefer_edit=False)

    @ctx.command("addroute", summary="新增归纳规则", usage="addroute 分组 关键词...", category="自动归纳", heavy=True)
    async def cmd_addroute(app, event, args):
        tokens = _shlex(args)
        if len(tokens) < 2:
            await ctx.reply(event, ui.panel("TG-Radar · 参数不足", [ui.section("示例", [f"<code>{app.config.cmd_prefix}addroute 分组 词A 词B</code>"])]), prefer_edit=False)
            return
        folder = app.find_folder(tokens[0]) or tokens[0]
        if ctx.db.get_folder(folder) is None:
            ctx.db.upsert_folder(folder, None, enabled=False)
        pattern = normalize_pattern_from_terms(tokens[1:])
        ctx.db.set_route(folder, pattern)
        app.queue_snapshot_flush()
        ctx.db.log_event("INFO", "ADD_ROUTE", f"{folder} -> {pattern}")
        await ctx.reply(event, ui.panel("TG-Radar · 归纳规则已保存", [ui.section("详情", [ui.bullet("分组", folder), ui.bullet("表达式", pattern)])]), prefer_edit=False)

    @ctx.command("delroute", summary="删除归纳规则", usage="delroute 分组", category="自动归纳", heavy=True)
    async def cmd_delroute(app, event, args):
        if not args:
            await ctx.reply(event, ui.panel("TG-Radar · 参数不足", [ui.section("示例", [f"<code>{app.config.cmd_prefix}delroute 分组</code>"])]), prefer_edit=False)
            return
        folder = app.find_folder(args) or args.strip()
        if not ctx.db.delete_route(folder):
            await ctx.reply(event, ui.panel("TG-Radar · 未找到规则", [ui.section("信息", [ui.bullet("分组", folder)])]), prefer_edit=False)
            return
        app.queue_snapshot_flush()
        ctx.db.log_event("INFO", "DELETE_ROUTE", folder)
        await ctx.reply(event, ui.panel("TG-Radar · 归纳规则已删除", [ui.section("结果", [ui.bullet("分组", folder)])]), prefer_edit=False)

    @ctx.command("sync", summary="手动同步", usage="sync", category="自动归纳", heavy=True)
    async def cmd_sync(app, event, args):
        await app.run_sync_command(event)

    @ctx.command("routescan", summary="手动归纳扫描", usage="routescan", category="自动归纳", heavy=True)
    async def cmd_routescan(app, event, args):
        await app.run_route_scan_command(event)
