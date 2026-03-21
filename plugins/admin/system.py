from __future__ import annotations

from ...config import load_config, update_config_data
from ...services.panels import render_job_accept_panel
from ...telegram_utils import bullet, escape, panel, section


def register(registry) -> None:
    @registry.command('setprefix', summary='修改 Telegram 命令前缀', usage='setprefix !', category='system', plugin='admin.system')
    async def setprefix_cmd(ctx):
        value = (ctx.args or '').strip()
        if not value or len(value) > 3 or ' ' in value or any(ch in value for ch in ['\\', '"', "'"]):
            await ctx.app.reply_panel(ctx.event, panel('命令前缀格式无效', [section('输入要求', [bullet('长度', '1-3 个字符', code=False), bullet('限制', '不能包含空格、引号、反斜杠', code=False)])]), auto_delete=0)
            return
        update_config_data(ctx.app.config.work_dir, {'cmd_prefix': value})
        ctx.app.config = load_config(ctx.app.config.work_dir)
        ctx.app.db.log_event('INFO', 'SET_PREFIX', value)
        await ctx.app.reply_panel(ctx.event, panel('命令前缀已更新', [section('新前缀', [bullet('命令前缀', value, code=False), bullet('试用命令', f'{value}help', code=False)])], '<i>新的前缀立即生效；后续命令请直接使用新前缀。</i>'), auto_delete=0)

    @registry.command('sync', summary='手动执行一次分组同步', usage='sync', category='system', heavy=True, plugin='admin.system')
    async def sync_cmd(ctx):
        await ctx.app.submit_heavy_job(ctx, 'sync_manual', priority=10, dedupe_key='sync_manual', delay_seconds=ctx.app.config.manual_heavy_delay_seconds, detail='将先同步分组与群组缓存，再按规则扫描自动归纳。')

    @registry.command('routescan', summary='手动执行一次自动归纳扫描', usage='routescan', category='system', heavy=True, plugin='admin.system')
    async def routescan_cmd(ctx):
        await ctx.app.submit_heavy_job(ctx, 'route_scan', priority=12, dedupe_key='route_scan', delay_seconds=ctx.app.config.manual_heavy_delay_seconds + 2, detail='只扫描自动归纳规则，不会阻塞轻命令。')

    @registry.command('update', summary='拉取仓库最新代码', usage='update', category='system', heavy=True, plugin='admin.system')
    async def update_cmd(ctx):
        if not (ctx.app.config.work_dir / '.git').exists():
            await ctx.app.reply_panel(ctx.event, panel('当前目录不是 git 仓库', [section('提示', ['· 请使用 git 方式部署后再执行 update。'])]), auto_delete=0)
            return
        await ctx.app.submit_heavy_job(ctx, 'update_repo', priority=15, dedupe_key='update_repo', delay_seconds=ctx.app.config.update_delay_seconds, detail='后台会执行 git pull --ff-only，完成后独立回包。')

    @registry.command('restart', summary='重启 admin/core 服务', usage='restart', category='system', heavy=True, plugin='admin.system')
    async def restart_cmd(ctx):
        ctx.app.write_last_message(ctx.event.id, 'restart')
        await ctx.app.submit_heavy_job(ctx, 'restart_services', priority=20, dedupe_key=None, delay_seconds=ctx.app.config.restart_delay_seconds, detail='systemd 已接管重启；服务恢复后会再次发送启动通知。')
