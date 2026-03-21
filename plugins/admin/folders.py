from __future__ import annotations

from ...telegram_utils import bullet, escape, panel, section


def register(registry) -> None:
    @registry.command('folders', summary='查看 TG 分组与缓存统计', usage='folders', category='folders', plugin='admin.folders')
    async def folders_cmd(ctx):
        await ctx.app.reply_panel(ctx.event, ctx.app.render_folders_message(), auto_delete=0)

    @registry.command('enable', summary='开启某个分组监听', usage='enable "分组名"', category='folders', plugin='admin.folders')
    async def enable_cmd(ctx):
        folder = await ctx.app.require_folder(ctx, allow_unknown=False)
        if folder is None:
            return
        ctx.app.db.set_folder_enabled(folder, True)
        ctx.app.queue_snapshot_flush()
        ctx.app.queue_core_reload('enable_folder', folder)
        ctx.app.db.log_event('INFO', 'ENABLE_FOLDER', folder)
        await ctx.app.reply_panel(ctx.event, panel('分组监控已开启', [section('当前动作', [bullet('分组', folder, code=False), bullet('状态', '开启', code=False)])]), auto_delete=0)

    @registry.command('disable', summary='关闭某个分组监听', usage='disable "分组名"', category='folders', plugin='admin.folders')
    async def disable_cmd(ctx):
        folder = await ctx.app.require_folder(ctx, allow_unknown=False)
        if folder is None:
            return
        ctx.app.db.set_folder_enabled(folder, False)
        ctx.app.queue_snapshot_flush()
        ctx.app.queue_core_reload('disable_folder', folder)
        ctx.app.db.log_event('INFO', 'DISABLE_FOLDER', folder)
        await ctx.app.reply_panel(ctx.event, panel('分组监控已关闭', [section('当前动作', [bullet('分组', folder, code=False), bullet('状态', '关闭', code=False)])]), auto_delete=0)
