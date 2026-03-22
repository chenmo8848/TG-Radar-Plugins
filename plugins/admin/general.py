PLUGIN_META = {"name": "general", "version": "6.0.0", "description": "通用面板与日志", "kind": "admin",
    "config_schema": {"panel_auto_delete_seconds": {"type": "int", "default": 45, "description": "面板自动删除秒数"}, "recycle_command_seconds": {"type": "int", "default": 8, "description": "源命令回收秒数"}}}

import shlex
from datetime import datetime
from tgr.plugin_sdk import PluginContext

def _sh(a):
    try: return shlex.split(a) if a else []
    except ValueError: return a.split()

def setup(ctx: PluginContext):
    ui = ctx.ui

    @ctx.command("ping", summary="在线心跳检测", usage="ping", category="通用")
    async def _(app, event, args):
        stats = ctx.db.get_runtime_stats()
        await ctx.reply(event, ui.panel("TG-Radar · 心跳", [ui.section("状态", [ui.bullet("运行", ui.format_duration((datetime.now() - app.started_at).total_seconds())), ui.bullet("命中", stats.get("total_hits", "0"))])]), auto_delete=12, prefer_edit=False)

    @ctx.command("status", summary="系统状态", usage="status", category="通用")
    async def _(app, event, args):
        await ctx.reply(event, app.render_status_message(), auto_delete=0, prefer_edit=False)

    @ctx.command("version", summary="版本信息", usage="version", category="通用")
    async def _(app, event, args):
        from tgr.version import __version__
        await ctx.reply(event, ui.panel("TG-Radar · 版本", [ui.section("信息", [ui.bullet("版本", __version__), ui.bullet("架构", "单进程 · 事件驱动 · 全解耦插件"), ui.bullet("模式", app.config.operation_mode)])]), prefer_edit=False)

    @ctx.command("config", summary="核心配置", usage="config", category="通用")
    async def _(app, event, args):
        await ctx.reply(event, app.render_config_message(), auto_delete=0, prefer_edit=False)

    @ctx.command("log", summary="事件日志", usage="log [important|normal|all] [数量]", category="通用")
    async def _(app, event, args):
        scope, limit = "important", 15
        for t in _sh(args):
            lo = t.lower()
            if lo in ("all", "full"): scope = "all"
            elif lo in ("normal", "recent"): scope = "normal"
            elif lo in ("important", "key"): scope = "important"
            elif t.isdigit(): limit = min(40, max(1, int(t)))
        rows = ctx.db.recent_logs_for_panel(limit=limit, scope=scope)
        if not rows:
            return await ctx.reply(event, ui.panel("TG-Radar · 事件", [ui.section("结果", ["<i>暂无记录</i>"])]), auto_delete=0, prefer_edit=False)
        blocks = []
        for r in rows:
            d = r["detail"][:109] + "…" if len(r["detail"]) > 110 else r["detail"]
            lines = [f"{r['icon']} <b>{r['title']}</b>", ui.soft_kv("时间", r["created_at"]), ui.soft_kv("摘要", r["summary"])]
            if d and d != r["summary"]: lines.append(ui.soft_kv("详情", d))
            blocks.append("\n".join(lines))
        await ctx.reply(event, ui.panel("TG-Radar · 事件日志", [ui.section("事件流", blocks)], f"<i><code>{ui.escape(app.config.cmd_prefix)}log all 20</code> 查看全部</i>"), auto_delete=0, prefer_edit=False)

    @ctx.command("jobs", summary="后台任务队列", usage="jobs", category="通用")
    async def _(app, event, args):
        await ctx.reply(event, app.render_jobs_message(), auto_delete=0, prefer_edit=False)
