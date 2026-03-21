PLUGIN_META = {"name": "folders", "version": "6.0.0", "description": "分组管理与启停", "kind": "admin"}
from tgr.plugin_sdk import PluginContext

def setup(ctx: PluginContext):
    ui = ctx.ui

    @ctx.command("folders", summary="查看全部分组", usage="folders", category="分组")
    async def _(app, event, args):
        rows = ctx.db.list_folders()
        if not rows: return await ctx.reply(event, ui.panel("TG-Radar · 分组", [ui.section("状态", ["<i>暂无分组，请先执行 sync</i>"])]), prefer_edit=False)
        cc, rc = ctx.db.count_cache_all_folders(), ctx.db.count_rules_all_folders()
        blocks = [f"{'🟢' if int(r['enabled']) else '⚪'} <b>{ui.escape(r['folder_name'])}</b>  {'开启' if int(r['enabled']) else '关闭'}  群 <code>{cc.get(r['folder_name'],0)}</code>  规则 <code>{rc.get(r['folder_name'],0)}</code>" for r in rows]
        await ctx.reply(event, ui.panel("TG-Radar · 分组总览", [ui.section("分组列表", blocks)]), auto_delete=75, prefer_edit=False)

    @ctx.command("rules", summary="查看分组规则", usage="rules 分组名", category="分组")
    async def _(app, event, args):
        if not args: return await ctx.reply(event, ui.panel("TG-Radar · 参数不足", [ui.section("用法", [f"<code>{app.config.cmd_prefix}rules 分组名</code>"])]), prefer_edit=False)
        f = app.find_folder(args)
        if not f: return await ctx.reply(event, ui.panel("TG-Radar · 找不到分组", []), prefer_edit=False)
        rows = ctx.db.get_rules_for_folder(f)
        if not rows: return await ctx.reply(event, ui.panel(f"TG-Radar · {f}", [ui.section("规则", ["<i>暂无规则</i>"])]), prefer_edit=False)
        blocks = [f"<b>{ui.escape(r['rule_name'])}</b>  <code>{ui.escape(r['pattern'])}</code>" for r in rows]
        await ctx.reply(event, ui.panel(f"TG-Radar · {f} 规则", [ui.section("已启用", blocks)]), auto_delete=80, prefer_edit=False)

    @ctx.command("enable", summary="开启分组监控", usage="enable 分组名", category="分组")
    async def _(app, event, args):
        if not args: return await ctx.reply(event, ui.panel("TG-Radar · 参数不足", []), prefer_edit=False)
        f = app.find_folder(args)
        if not f: return await ctx.reply(event, ui.panel("TG-Radar · 找不到分组", []), prefer_edit=False)
        ctx.db.set_folder_enabled(f, True); app.queue_snapshot_flush(); app.queue_core_reload("enable", f)
        ctx.db.log_event("INFO", "ENABLE_FOLDER", f)
        await ctx.emit("folder_changed", {"folder": f, "action": "enable"})
        await ctx.reply(event, ui.panel("TG-Radar · 分组已开启", [ui.section("结果", [ui.bullet("分组", f), ui.bullet("状态", "已开启")])]), prefer_edit=False)

    @ctx.command("disable", summary="关闭分组监控", usage="disable 分组名", category="分组")
    async def _(app, event, args):
        if not args: return await ctx.reply(event, ui.panel("TG-Radar · 参数不足", []), prefer_edit=False)
        f = app.find_folder(args)
        if not f: return await ctx.reply(event, ui.panel("TG-Radar · 找不到分组", []), prefer_edit=False)
        ctx.db.set_folder_enabled(f, False); app.queue_snapshot_flush(); app.queue_core_reload("disable", f)
        ctx.db.log_event("INFO", "DISABLE_FOLDER", f)
        await ctx.emit("folder_changed", {"folder": f, "action": "disable"})
        await ctx.reply(event, ui.panel("TG-Radar · 分组已关闭", [ui.section("结果", [ui.bullet("分组", f), ui.bullet("状态", "已关闭")])]), prefer_edit=False)
