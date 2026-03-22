"""系统重启与更新。"""

PLUGIN_META = {
    "name": "system",
    "version": "6.0.0",
    "description": "系统重启与更新",
    "kind": "admin",
    "config_schema": {
        "restart_delay_seconds": {"type": "float", "default": 2.0, "description": "重启延迟秒数"},
    },
}

from tgr.plugin_sdk import PluginContext


def setup(ctx: PluginContext):
    ui = ctx.ui

    @ctx.command("restart", summary="重启服务", usage="restart", category="系统任务", heavy=True)
    async def cmd_restart(app, event, args):
        delay = ctx.config.get("restart_delay_seconds", 2.0)
        app.write_last_message(event.id, "restart")
        result = ctx.bus.submit_job(
            "restart_services",
            payload={"reply_to": int(event.id), "delay": delay, "trace": app._event_trace(event)},
            priority=20, dedupe_key="restart_services", origin="telegram", visible=True,
            delay_seconds=delay,
        )
        ctx.db.log_event("INFO", "JOB_QUEUE", f"{app._event_trace(event)} restart queued")
        title = "TG-Radar · 重启任务已接收" if result and result.created else "TG-Radar · 重启任务已在后台"
        await ctx.reply(event, ui.panel(title, [ui.section("说明", [
            "· 服务将重启。",
            "· 未完成的归纳任务会保留。",
        ])]), auto_delete=0)

    @ctx.command("update", summary="更新核心与插件仓库", usage="update", category="系统任务", heavy=True)
    async def cmd_update(app, event, args):
        await app.run_update_command(event)
