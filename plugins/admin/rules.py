"""规则维护与通知设置。"""

PLUGIN_META = {
    "name": "rules",
    "version": "6.0.0",
    "description": "规则维护与通知设置",
    "kind": "admin",
}

import re
import shlex
from tgr.plugin_sdk import PluginContext, normalize_pattern_from_terms, merge_patterns, split_terms, try_remove_terms_from_pattern

_SAFE_PREFIX = re.compile(r"^[^\s\\\"'<>&]{1,3}$")


def _shlex(args: str) -> list[str]:
    try:
        return shlex.split(args) if args else []
    except ValueError:
        return args.split()


def setup(ctx: PluginContext):
    ui = ctx.ui

    @ctx.command("addrule", summary="追加词项到规则", usage="addrule 分组 规则名 关键词...", category="规则维护", heavy=True)
    async def cmd_addrule(app, event, args):
        tokens = _shlex(args)
        if len(tokens) < 3:
            await ctx.reply(event, ui.panel("TG-Radar · 参数不足", [ui.section("示例", [f"<code>{app.config.cmd_prefix}addrule 分组 规则A 词A 词B</code>"])]), prefer_edit=False)
            return
        folder = app.find_folder(tokens[0]) or tokens[0]
        rule_name = tokens[1]
        incoming = normalize_pattern_from_terms(tokens[2:])
        if ctx.db.get_folder(folder) is None:
            ctx.db.upsert_folder(folder, None, enabled=False)
        existing = ctx.db.get_rules_for_folder(folder)
        old = next((r for r in existing if r["rule_name"] == rule_name), None)
        merged = merge_patterns(old["pattern"] if old else None, incoming)
        ctx.db.upsert_rule(folder, rule_name, merged)
        app.queue_snapshot_flush()
        app.queue_core_reload("add_rule", f"{folder}/{rule_name}")
        ctx.db.log_event("INFO", "UPDATE_RULE" if old else "ADD_RULE", f"{folder}/{rule_name} -> {merged}")
        await ctx.emit("rule_changed", {"folder": folder, "rule": rule_name, "action": "add"})
        preview = " / ".join(split_terms(tokens[2:])[:6])
        await ctx.reply(event, ui.panel("TG-Radar · 规则已追加", [ui.section("详情", [ui.bullet("分组", folder), ui.bullet("规则", rule_name), ui.bullet("新增", preview, code=False), ui.bullet("表达式", merged)])]), prefer_edit=False)

    @ctx.command("setrule", summary="覆盖整条规则", usage="setrule 分组 规则名 表达式", category="规则维护", heavy=True)
    async def cmd_setrule(app, event, args):
        tokens = _shlex(args)
        if len(tokens) < 3:
            await ctx.reply(event, ui.panel("TG-Radar · 参数不足", [ui.section("示例", [f"<code>{app.config.cmd_prefix}setrule 分组 规则A 表达式</code>"])]), prefer_edit=False)
            return
        folder = app.find_folder(tokens[0]) or tokens[0]
        rule_name, pattern = tokens[1], normalize_pattern_from_terms(tokens[2:])
        if ctx.db.get_folder(folder) is None:
            ctx.db.upsert_folder(folder, None, enabled=False)
        ctx.db.upsert_rule(folder, rule_name, pattern)
        app.queue_snapshot_flush()
        app.queue_core_reload("set_rule", f"{folder}/{rule_name}")
        ctx.db.log_event("INFO", "UPDATE_RULE", f"{folder}/{rule_name} -> {pattern}")
        await ctx.emit("rule_changed", {"folder": folder, "rule": rule_name, "action": "set"})
        await ctx.reply(event, ui.panel("TG-Radar · 规则已覆盖", [ui.section("详情", [ui.bullet("分组", folder), ui.bullet("规则", rule_name), ui.bullet("表达式", pattern)])]), prefer_edit=False)

    @ctx.command("delrule", summary="删除规则或部分词项", usage="delrule 分组 规则名 [词...]", category="规则维护", heavy=True)
    async def cmd_delrule(app, event, args):
        tokens = _shlex(args)
        if len(tokens) < 2:
            await ctx.reply(event, ui.panel("TG-Radar · 参数不足", [ui.section("示例", [f"<code>{app.config.cmd_prefix}delrule 分组 规则A</code>"])]), prefer_edit=False)
            return
        folder = app.find_folder(tokens[0]) or tokens[0]
        rule_name, terms = tokens[1], tokens[2:]
        existing = ctx.db.get_rules_for_folder(folder)
        rule = next((r for r in existing if r["rule_name"] == rule_name), None)
        if not rule:
            await ctx.reply(event, ui.panel("TG-Radar · 找不到规则", [ui.section("信息", [ui.bullet("分组", folder), ui.bullet("规则", rule_name)])]), prefer_edit=False)
            return
        if not terms:
            ctx.db.delete_rule(folder, rule_name)
            app.queue_snapshot_flush()
            app.queue_core_reload("delete_rule", f"{folder}/{rule_name}")
            ctx.db.log_event("INFO", "DELETE_RULE", f"{folder}/{rule_name}")
            await ctx.emit("rule_changed", {"folder": folder, "rule": rule_name, "action": "delete"})
            await ctx.reply(event, ui.panel("TG-Radar · 规则已删除", [ui.section("结果", [ui.bullet("分组", folder), ui.bullet("规则", rule_name)])]), prefer_edit=False)
            return
        new_pat = try_remove_terms_from_pattern(rule["pattern"], terms)
        if not new_pat:
            ctx.db.delete_rule(folder, rule_name)
            app.queue_snapshot_flush()
            app.queue_core_reload("clear_rule", f"{folder}/{rule_name}")
            await ctx.reply(event, ui.panel("TG-Radar · 规则已清空并删除", []), prefer_edit=False)
            return
        ctx.db.update_rule_pattern(folder, rule_name, new_pat)
        app.queue_snapshot_flush()
        app.queue_core_reload("update_rule", f"{folder}/{rule_name}")
        ctx.db.log_event("INFO", "UPDATE_RULE", f"{folder}/{rule_name} -> {new_pat}")
        await ctx.reply(event, ui.panel("TG-Radar · 规则已更新", [ui.section("新表达式", [f"<code>{ui.escape(new_pat)}</code>"])]), prefer_edit=False)

    @ctx.command("setnotify", summary="设置系统通知目标", usage="setnotify ID/off", category="规则维护", heavy=True)
    async def cmd_setnotify(app, event, args):
        from tgr.config import load_config, update_config_data
        value = app.parse_int_or_none(args)
        update_config_data(app.config.work_dir, {"notify_channel_id": value})
        app.config = load_config(app.config.work_dir)
        ctx.db.log_event("INFO", "SET_NOTIFY", str(value))
        await ctx.reply(event, ui.panel("TG-Radar · 通知目标已更新", [ui.section("配置", [ui.bullet("去向", value or "Saved Messages")])]), prefer_edit=False)

    @ctx.command("setalert", summary="设置默认告警目标", usage="setalert ID/off", category="规则维护", heavy=True)
    async def cmd_setalert(app, event, args):
        from tgr.config import load_config, update_config_data
        value = app.parse_int_or_none(args)
        update_config_data(app.config.work_dir, {"global_alert_channel_id": value})
        app.config = load_config(app.config.work_dir)
        app.queue_core_reload("set_alert", str(value))
        ctx.db.log_event("INFO", "SET_ALERT", str(value))
        await ctx.reply(event, ui.panel("TG-Radar · 告警目标已更新", [ui.section("配置", [ui.bullet("默认告警", value or "未设置")])]), prefer_edit=False)

    @ctx.command("setprefix", summary="修改命令前缀", usage="setprefix 新前缀", category="规则维护", heavy=True)
    async def cmd_setprefix(app, event, args):
        from tgr.config import update_config_data
        value = args.strip()
        if not value or not _SAFE_PREFIX.match(value):
            await ctx.reply(event, ui.panel("TG-Radar · 前缀无效", [ui.section("要求", ["· 1-3字符，不含空格/引号/HTML字符"])]), prefer_edit=False)
            return
        update_config_data(app.config.work_dir, {"cmd_prefix": value})
        ctx.db.log_event("INFO", "SET_PREFIX", value)
        app.write_last_message(event.id, "restart")
        await ctx.reply(event, ui.panel("TG-Radar · 前缀已更新", [ui.section("新前缀", [ui.bullet("前缀", value), ui.bullet("试用", f"{value}help")])], "<i>即将自动重启。</i>"), auto_delete=0, prefer_edit=False)
        app.restart_services(delay=1.2)
