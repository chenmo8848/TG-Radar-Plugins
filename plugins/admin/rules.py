from __future__ import annotations

import shlex

from ...telegram_utils import bullet, escape, panel, section, merge_patterns, normalize_pattern_from_terms, split_terms, try_remove_terms_from_pattern


def _parse_tokens(text: str) -> list[str]:
    try:
        return shlex.split(text) if text else []
    except Exception:
        return [part for part in (text or '').split() if part]


def register(registry) -> None:
    @registry.command('rules', summary='查看指定分组规则', usage='rules "分组名"', category='rules', plugin='admin.rules')
    async def rules_cmd(ctx):
        folder = await ctx.app.require_folder(ctx, allow_unknown=False)
        if folder is None:
            return
        await ctx.app.reply_panel(ctx.event, ctx.app.render_rules_message(folder), auto_delete=0)

    @registry.command('addrule', summary='新增规则或向同名规则追加关键词', usage='addrule "分组名" "规则名" 关键词A 关键词B', category='rules', plugin='admin.rules')
    async def addrule_cmd(ctx):
        tokens = _parse_tokens(ctx.args)
        if len(tokens) < 3:
            await ctx.app.reply_panel(ctx.event, panel('参数不足', [section('示例', [f'<code>{escape(ctx.app.config.cmd_prefix)}addrule "示例分组" "规则A" 关键词A 关键词B</code>'])]), auto_delete=0)
            return
        folder = ctx.app.find_folder(tokens[0]) or tokens[0]
        rule_name = tokens[1]
        incoming = normalize_pattern_from_terms(tokens[2:])
        if ctx.app.db.get_folder(folder) is None:
            ctx.app.db.upsert_folder(folder, None, enabled=False)
        existing_rows = ctx.app.db.get_rules_for_folder(folder)
        existing_rule = next((row for row in existing_rows if row['rule_name'] == rule_name), None)
        merged_pattern = merge_patterns(existing_rule['pattern'] if existing_rule else None, incoming)
        ctx.app.db.upsert_rule(folder, rule_name, merged_pattern)
        ctx.app.queue_snapshot_flush()
        ctx.app.queue_core_reload('add_rule', f'{folder}/{rule_name}')
        ctx.app.db.log_event('INFO', 'UPDATE_RULE' if existing_rule else 'ADD_RULE', f'{folder}/{rule_name} -> {merged_pattern}')
        await ctx.app.reply_panel(ctx.event, panel('规则已保存', [section('规则详情', [bullet('分组', folder, code=False), bullet('规则名', rule_name, code=False), bullet('表达式', merged_pattern)])]), auto_delete=0)

    @registry.command('setrule', summary='整体覆盖一条规则', usage='setrule "分组名" "规则名" 新表达式', category='rules', plugin='admin.rules')
    async def setrule_cmd(ctx):
        tokens = _parse_tokens(ctx.args)
        if len(tokens) < 3:
            await ctx.app.reply_panel(ctx.event, panel('参数不足', [section('示例', [f'<code>{escape(ctx.app.config.cmd_prefix)}setrule "示例分组" "规则A" 新表达式</code>'])]), auto_delete=0)
            return
        folder = ctx.app.find_folder(tokens[0]) or tokens[0]
        rule_name = tokens[1]
        pattern = normalize_pattern_from_terms(tokens[2:])
        if ctx.app.db.get_folder(folder) is None:
            ctx.app.db.upsert_folder(folder, None, enabled=False)
        ctx.app.db.upsert_rule(folder, rule_name, pattern)
        ctx.app.queue_snapshot_flush()
        ctx.app.queue_core_reload('set_rule', f'{folder}/{rule_name}')
        ctx.app.db.log_event('INFO', 'UPDATE_RULE', f'{folder}/{rule_name} -> {pattern}')
        await ctx.app.reply_panel(ctx.event, panel('规则已覆盖', [section('规则详情', [bullet('分组', folder, code=False), bullet('规则名', rule_name, code=False), bullet('表达式', pattern)])]), auto_delete=0)

    @registry.command('delrule', summary='删除整条规则，或只删除规则中的部分词项', usage='delrule "分组名" "规则名" [词A 词B]', category='rules', plugin='admin.rules')
    async def delrule_cmd(ctx):
        tokens = _parse_tokens(ctx.args)
        if len(tokens) < 2:
            await ctx.app.reply_panel(ctx.event, panel('参数不足', [section('示例', [f'<code>{escape(ctx.app.config.cmd_prefix)}delrule "示例分组" "规则A"</code>', f'<code>{escape(ctx.app.config.cmd_prefix)}delrule "示例分组" "规则A" 关键词A</code>'])]), auto_delete=0)
            return
        folder = ctx.app.find_folder(tokens[0]) or tokens[0]
        rule_name = tokens[1]
        rows = ctx.app.db.get_rules_for_folder(folder)
        rule = next((row for row in rows if row['rule_name'] == rule_name), None)
        if rule is None:
            await ctx.app.reply_panel(ctx.event, panel('找不到该规则', [section('定位信息', [bullet('分组', folder, code=False), bullet('规则名', rule_name, code=False)])]), auto_delete=0)
            return
        terms = tokens[2:]
        if not terms:
            ctx.app.db.delete_rule(folder, rule_name)
            ctx.app.queue_snapshot_flush()
            ctx.app.queue_core_reload('delete_rule', f'{folder}/{rule_name}')
            ctx.app.db.log_event('INFO', 'DELETE_RULE', f'{folder}/{rule_name}')
            await ctx.app.reply_panel(ctx.event, panel('规则已删除', [section('删除结果', [bullet('分组', folder, code=False), bullet('规则名', rule_name, code=False)])]), auto_delete=0)
            return
        new_pattern = try_remove_terms_from_pattern(rule['pattern'], split_terms(terms))
        if not new_pattern:
            ctx.app.db.delete_rule(folder, rule_name)
            ctx.app.db.log_event('INFO', 'DELETE_RULE', f'{folder}/{rule_name}')
            title = '规则项已全部移除'
            rows_out = [bullet('分组', folder, code=False), bullet('规则名', rule_name, code=False)]
        else:
            ctx.app.db.update_rule_pattern(folder, rule_name, new_pattern)
            ctx.app.db.log_event('INFO', 'UPDATE_RULE', f'{folder}/{rule_name} -> {new_pattern}')
            title = '规则已裁剪'
            rows_out = [bullet('分组', folder, code=False), bullet('规则名', rule_name, code=False), bullet('新表达式', new_pattern)]
        ctx.app.queue_snapshot_flush()
        ctx.app.queue_core_reload('trim_rule', f'{folder}/{rule_name}')
        await ctx.app.reply_panel(ctx.event, panel(title, [section('处理结果', rows_out)]), auto_delete=0)
