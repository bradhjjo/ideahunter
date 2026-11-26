#!/usr/bin/env python3
"""
Pipeline orchestrator.

Runs the four pipeline stages in-process (no subprocess), with structured
logging and cross-source URL deduplication between news and trends.
"""

import logging
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

import fetch_news_rss
import fetch_trends
import analyze_ideas
import send_telegram_message

log = logging.getLogger("ideahunter")


def _configure_logging() -> None:
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _run(stage: str, fn) -> bool:
    log.info("---- %s ----", stage)
    try:
        ok = bool(fn())
    except Exception:
        log.exception("stage %r raised", stage)
        return False
    log.info("%s: %s", stage, "OK" if ok else "FAILED")
    return ok


def _cross_dedup_trends_against_news() -> None:
    """Drop any trend item whose URL already appears in the news file.

    Hacker News / YC Launch posts can show up in both feeds; keeping only the
    news copy avoids duplicate context being fed to the LLM.
    """
    import json
    tmp = os.path.join(os.path.dirname(__file__), "..", ".tmp")
    news_path = os.path.join(tmp, "ai_news.json")
    trends_path = os.path.join(tmp, "ai_trends.json")
    if not (os.path.exists(news_path) and os.path.exists(trends_path)):
        return

    with open(news_path, encoding="utf-8") as f:
        news_urls = {a.get("url") for a in json.load(f) if a.get("url")}
    with open(trends_path, encoding="utf-8") as f:
        trends = json.load(f)

    before = len(trends)
    trends = [t for t in trends if t.get("url") not in news_urls]
    removed = before - len(trends)
    if removed:
        with open(trends_path, "w", encoding="utf-8") as f:
            json.dump(trends, f, ensure_ascii=False, indent=2)
        log.info("cross-dedup: removed %d trend(s) duplicating news URLs", removed)


def main() -> int:
    _configure_logging()
    log.info("IdeaHunter pipeline starting at %s", datetime.now().isoformat(timespec="seconds"))

    stages = [
        ("fetch_news_rss",        fetch_news_rss.main),
        ("fetch_trends",          fetch_trends.main),
        ("cross_dedup",           lambda: (_cross_dedup_trends_against_news(), True)[1]),
        ("analyze_ideas",         analyze_ideas.main),
        ("send_telegram_message", send_telegram_message.main),
    ]

    results = [(name, _run(name, fn)) for name, fn in stages]

    log.info("---- summary ----")
    for name, ok in results:
        log.info("  %s: %s", name, "OK" if ok else "FAILED")
    log.info("IdeaHunter pipeline finished at %s", datetime.now().isoformat(timespec="seconds"))

    return 0 if all(ok for _, ok in results) else 1


if __name__ == "__main__":
    sys.exit(main())
