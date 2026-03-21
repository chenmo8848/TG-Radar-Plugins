from __future__ import annotations

import shlex

from ...config import load_config, update_config_data
from ...telegram_utils import bullet, escape, panel, section, normalize_pattern_from_terms


def _parse_tokens(text: str) -> list[str]:
    try:
        return shlex.split(text) if text else []
    except Exception:
        return [part for part in (text or '').split() if part]


def register(registry) -> None:
    @registry.command('routes', summary='查看自动归纳 / 收纳规则', usage='routes', category='routes', plugin='admin.routes')
    async def routes_cmd(ctx):
        await ctx.app.reply_panel(ctx.event, ctx.app.render_routes_message(), auto_delete=0)

    @registry.command('addroute', summary='新增自动归纳规则', usage='addroute "分组名" 标题词A 标题词B', category='routes', plugin='admin.routes')
    async def addroute_cmd(ctx):
        tokens = _parse_tokens(ctx.args)
        if len(tokens) < 2:
            await ctx.app.reply_panel(ctx.event, panel('参数不足', [section('示例', [f'<code>{escape(ctx.app.config.cmd_prefix)}addroute "示例分组" 标题词A 标题词B</code>'])]), auto_delete=0)
            return
        folder = ctx.app.find_folder(tokens[0]) or tokens[0]
        pattern = normalize_pattern_from_terms(tokens[1:])
        if ctx.app.db.get_folder(folder) is None:
            ctx.app.db.upsert_folder(folder, None, enabled=False)
        ctx.app.db.set_route(folder, pattern)
        ctx.app.queue_snapshot_flush()
        ctx.app.db.log_event('INFO', 'ADD_ROUTE', f'{folder} -> {pattern}')
        await ctx.app.reply_panel(ctx.event, panel('自动归纳规则已保存', [section('规则详情', [bullet('分组', folder, code=False), bullet('路由表达式', pattern)])]), auto_delete=0)

    @registry.command('delroute', summary='删除自动归纳规则', usage='delroute "分组名"', category='routes', plugin='admin.routes')
    async def delroute_cmd(ctx):
        tokens = _parse_tokens(ctx.args)
        if len(tokens) < 1:
            await ctx.app.reply_panel(ctx.event, panel('参数不足', [section('示例', [f'<code>{escape(ctx.app.config.cmd_prefix)}delroute "示例分组"</code>'])]), auto_delete=0)
            return
        folder = ctx.app.find_folder(tokens[0]) or tokens[0]
        if not ctx.app.db.delete_route(folder):
            await ctx.app.reply_panel(ctx.event, panel('没有找到该自动归纳规则', [section('定位信息', [bullet('分组', folder, code=False)])]), auto_delete=0)
            return
        ctx.app.queue_snapshot_flush()
        ctx.app.db.log_event('INFO', 'DELETE_ROUTE', folder)
        await ctx.app.reply_panel(ctx.event, panel('自动归纳规则已删除', [section('删除结果', [bullet('分组', folder, code=False)])]), auto_delete=0)

    @registry.command('setnotify', summary='设置系统通知目标', usage='setnotify -1001234567890 | setnotify off', category='routes', plugin='admin.routes')
    async def setnotify_cmd(ctx):
        value = ctx.app.parse_int_or_none(ctx.args.strip())
        update_config_data(ctx.app.config.work_dir, {'notify_channel_id': value})
        ctx.app.config = load_config(ctx.app.config.work_dir)
        ctx.app.db.log_event('INFO', 'SET_NOTIFY', str(value))
        await ctx.app.reply_panel(ctx.event, panel('系统通知目标已更新', [section('新配置', [bullet('系统通知', value if value is not None else 'Saved Messages', code=False)])]), auto_delete=0)

    @registry.command('setalert', summary='设置默认告警目标', usage='setalert -1001234567890 | setalert off', category='routes', plugin='admin.routes')
    async def setalert_cmd(ctx):
        value = ctx.app.parse_int_or_none(ctx.args.strip())
        update_config_data(ctx.app.config.work_dir, {'global_alert_channel_id': value})
        ctx.app.config = load_config(ctx.app.config.work_dir)
        ctx.app.queue_core_reload('set_alert', str(value))
        ctx.app.db.log_event('INFO', 'SET_ALERT', str(value))
        await ctx.app.reply_panel(ctx.event, panel('默认告警频道已更新', [section('新配置', [bullet('默认告警', value if value is not None else '未设置', code=False), bullet('生效范围', '未单独配置告警频道的分组', code=False)])]), auto_delete=0)
