#!/usr/bin/env python3
"""
Telegram message delivery script (IdeaHunter).
Formats and sends the daily LLM report to a Telegram chat/channel.
"""

import json
import os
from datetime import datetime
from typing import List
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import asyncio
from dotenv import load_dotenv

try:
    load_dotenv()
except Exception:
    pass


# Telegram caps each message at 4096 characters (HTML included).
TELEGRAM_MAX_LEN = 4096


def _provider_label(report: dict) -> str:
    """Human-readable label for the LLM that generated the report."""
    provider = (report.get('llm_provider') or '').lower()
    if provider == 'gemini':
        model = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        return f"Gemini ({model})"
    if provider == 'local':
        model = os.getenv('LOCAL_LLM_MODEL', 'local-model')
        return f"Local LLM ({model})"
    return provider or 'LLM'


def format_llm_report(report: dict) -> str:
    """Format the LLM analysis report as Telegram HTML."""
    lines = []

    # Header
    lines.append("💡 <b>AI Product Idea Hunter</b>")
    lines.append(f"📅 {report['date']}")
    lines.append(f"🤖 <i>Powered by {_provider_label(report)}</i>")
    lines.append("")

    # Data source summary
    news_count = report.get('news_count', 0)
    social_count = report.get('social_count', 0)
    lines.append(f"📊 <b>Trends analyzed:</b> {news_count} news articles | {social_count} community posts")
    lines.append("")

    analysis = report.get('llm_analysis', {})

    # Executive summary
    exec_summary = analysis.get('executive_summary', '')
    if exec_summary:
        lines.append("📋 <b>Today's Trend Summary</b>")
        lines.append(exec_summary)
        lines.append("")

    # Top themes
    themes = analysis.get('top_themes', [])
    if themes:
        themes_str = ' '.join([f"#{t.replace(' ', '_')}" for t in themes[:5]])
        lines.append("🔥 <b>Top Themes</b>")
        lines.append(themes_str)
        lines.append("")

    # Product ideas
    ideas = analysis.get('product_ideas', [])
    if ideas:
        lines.append("🎯 <b>Today's Top 5 AI Product Ideas</b>")
        lines.append("")

        for i, idea in enumerate(ideas[:5], 1):
            lines.append(f"<b>{i}. {idea.get('idea_name', 'Idea')}</b>")
            lines.append(f"<i>{idea.get('description', '')}</i>")
            lines.append(f"• <b>Target:</b> {idea.get('target_users', '')}")
            lines.append(f"• <b>Why Now:</b> {idea.get('why_now', '')}")
            lines.append(f"• <b>Start Today:</b> {idea.get('actionable_step_1', '')}")
            lines.append("")

    return '\n'.join(lines)


def split_for_telegram(message: str, limit: int = TELEGRAM_MAX_LEN) -> List[str]:
    """Split a long HTML message into <=limit chunks on line boundaries.

    Slicing mid-tag (e.g. inside `<b>...`) makes Telegram reject the message
    with parse_mode=HTML. Since format_llm_report only opens and closes tags
    within a single line, splitting on '\n' guarantees each chunk is valid HTML.
    """
    if len(message) <= limit:
        return [message]

    chunks: List[str] = []
    current = ""
    for line in message.split('\n'):
        candidate = f"{current}\n{line}" if current else line
        if len(candidate) <= limit:
            current = candidate
            continue
        if current:
            chunks.append(current)
        # A single line longer than the limit is rare here, but guard anyway.
        while len(line) > limit:
            chunks.append(line[:limit])
            line = line[limit:]
        current = line
    if current:
        chunks.append(current)
    return chunks


async def send_telegram_message(bot_token: str, chat_id: str, message: str, max_retries: int = 3):
    """Send message to Telegram (async), splitting on line boundaries if needed."""
    bot = Bot(token=bot_token)
    chunks = split_for_telegram(message)

    for chunk in chunks:
        for attempt in range(max_retries):
            try:
                await bot.send_message(
                    chat_id=chat_id,
                    text=chunk,
                    parse_mode=ParseMode.HTML,
                    disable_web_page_preview=True,
                )
                print(f"✓ Sent chunk ({len(chunk)} chars)")
                break
            except TelegramError as e:
                print(f"✗ Attempt {attempt+1}/{max_retries} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise


def main():
    """Main entry point."""
    print("📱 Starting Telegram message delivery (IdeaHunter)...")

    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not bot_token or not chat_id:
        print("❌ Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID environment variables")
        return False

    # Load LLM report
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(script_dir, '..', '.tmp')
    report_file = os.path.join(tmp_dir, 'llm_report.json')

    if not os.path.exists(report_file):
        print(f"❌ Report file not found: {report_file}")
        return False

    with open(report_file, 'r', encoding='utf-8') as f:
        report = json.load(f)

    message = format_llm_report(report)

    try:
        asyncio.run(send_telegram_message(bot_token, chat_id, message))
        print("✅ Telegram message sent successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to send Telegram message: {e}")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
