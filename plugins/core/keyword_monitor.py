from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime

from ...telegram_utils import blockquote_preview, bullet, build_message_link, escape, html_code, panel, section


@dataclass
class RuntimeState:
    target_map: dict[int, list[dict]]
    valid_rules_count: int
    revision: int
    started_at: datetime


@dataclass
class RuleHit:
    rule_name: str
    total_count: int
    first_hit: str


def display_sender_name(sender: object | None, fallback: str = '未知用户') -> str:
    if sender is None:
        return fallback
    username = getattr(sender, 'username', None)
    if username:
        return '@' + str(username).lstrip('@')
    first = (getattr(sender, 'first_name', None) or '').strip()
    last = (getattr(sender, 'last_name', None) or '').strip()
    full = (first + (' ' + last if last else '')).strip()
    return full or fallback


def severity_label(rule_count: int, total_hits: int) -> tuple[str, str]:
    if rule_count >= 3 or total_hits >= 8:
        return '高优先级', '🔥'
    if rule_count >= 2 or total_hits >= 4:
        return '高关注', '🚨'
    return '常规命中', '⚠️'


def collect_rule_hits(pattern: re.Pattern[str], text: str, max_collect: int = 20) -> tuple[int, str | None]:
    count = 0
    first_hit: str | None = None
    for idx, match in enumerate(pattern.finditer(text)):
        if idx >= max_collect:
            count += 1
            continue
        count += 1
        if first_hit is None:
            first_hit = match.group(0)
    return count, first_hit


def compile_target_map(raw_target_map: dict[int, list[dict]], logger) -> dict[int, list[dict]]:
    compiled: dict[int, list[dict]] = {}
    for chat_id, tasks in raw_target_map.items():
        bucket: list[dict] = []
        for task in tasks:
            rules = []
            for rule_name, pattern in task['rules']:
                try:
                    rules.append((str(rule_name), re.compile(str(pattern), re.IGNORECASE)))
                except re.error as exc:
                    logger.warning('invalid regex folder=%s rule=%s: %s', task.get('folder_name'), rule_name, exc)
            if not rules:
                continue
            bucket.append({
                'folder_name': str(task['folder_name']),
                'alert_channel': int(task['alert_channel']),
                'rules': rules,
            })
        if bucket:
            compiled[int(chat_id)] = bucket
    return compiled


def render_alert_message(*, folder_name: str, chat_title: str, sender_name: str, msg_link: str, msg_text: str, rule_hits: list[RuleHit]) -> str:
    total_hits = sum(item.total_count for item in rule_hits)
    severity, icon = severity_label(len(rule_hits), total_hits)
    detail_rows: list[str] = []
    for item in rule_hits[:4]:
        detail_rows.append(f'· {escape(item.rule_name)}：{html_code(item.first_hit)} × {html_code(item.total_count)}')
    if len(rule_hits) > 4:
        detail_rows.append(f'· 其余规则：{html_code("+" + str(len(rule_hits) - 4))}')
    footer = f'{icon} <a href="{msg_link}">打开原始消息</a>' if msg_link else f'{icon} <i>当前消息不支持直达链接</i>'
    return panel('TG-Radar 命中告警', [
        section('命中摘要', [
            bullet('等级', severity, code=False),
            bullet('分组', folder_name, code=False),
            bullet('来源', chat_title, code=False),
            bullet('发送者', sender_name, code=False),
            bullet('时间', datetime.now().strftime('%m-%d %H:%M:%S'), code=False),
        ]),
        section('命中详情', detail_rows),
        section('消息预览', [blockquote_preview(msg_text, 760)]),
    ], footer)


def reload_runtime_state(db, alert_channel_id: int | None, logger, state: RuntimeState) -> RuntimeState:
    raw_target_map, valid_rules_count = db.build_target_map(alert_channel_id)
    compiled = compile_target_map(raw_target_map, logger)
    return RuntimeState(target_map=compiled, valid_rules_count=valid_rules_count, revision=db.get_revision(), started_at=state.started_at)
