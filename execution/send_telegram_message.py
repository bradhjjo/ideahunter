#!/usr/bin/env python3
"""
Telegram message delivery script (IdeaHunter).
Formats and sends the daily LLM report to a Telegram chat/channel.
"""

import json
import os
from datetime import datetime
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError
import asyncio
from dotenv import load_dotenv

try:
    load_dotenv()
except:
    pass


def format_llm_report(report: dict) -> str:
    """Format the LLM analysis report as Telegram HTML."""
    lines = []

    # Header
    lines.append("💡 <b>AI Product Idea Hunter</b>")
    lines.append(f"📅 {report['date']}")
    lines.append("🤖 <i>Powered by Gemini 2.5 Flash</i>")
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


async def send_telegram_message(bot_token: str, chat_id: str, message: str, max_retries: int = 3):
    """Send message to Telegram (async). Respects Telegram's 4096-char limit."""
    bot = Bot(token=bot_token)

    for attempt in range(max_retries):
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=message[:4096],
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            print("✓ Message sent successfully")
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
