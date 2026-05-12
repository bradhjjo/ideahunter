#!/usr/bin/env python3
"""
AI News RSS Fetcher.
Collects articles from major AI news/blog/newsletter RSS feeds.
Results are saved to .tmp/ai_news.json.

To add more sources, append entries to the `feeds` dict inside fetch_ai_news_rss().
"""

import feedparser
import json
import os
from calendar import timegm
from datetime import datetime, timedelta, timezone
from typing import List, Dict
import time


# Drop RSS entries older than this many days when a usable timestamp exists.
MAX_AGE_DAYS = int(os.getenv("NEWS_MAX_AGE_DAYS", "7"))


def _entry_is_fresh(entry, max_age_days: int = MAX_AGE_DAYS) -> bool:
    """Return True if the entry has no usable timestamp or is within the window."""
    published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
    if not published_struct:
        return True  # no date → keep, let the LLM decide
    try:
        published = datetime.fromtimestamp(timegm(published_struct), tz=timezone.utc)
    except (TypeError, ValueError, OverflowError):
        return True
    return (datetime.now(timezone.utc) - published) <= timedelta(days=max_age_days)


def fetch_ai_news_rss() -> List[Dict]:
    """Fetch articles from AI news/newsletter RSS feeds.

    Add or remove sources in the dict below as needed.
    All entries use standard RSS — no API keys required.
    Items older than NEWS_MAX_AGE_DAYS (default 7) are dropped when the feed
    provides a parseable date.
    """
    articles = []

    feeds = {
        # ── Curated AI newsletters ──────────────────────────────────────────
        'TLDR AI':              'https://tldr.tech/rss/ai',
        "Ben's Bites":          'https://bensbites.beehiiv.com/feed',
        'Import AI':            'https://importai.substack.com/feed',
        'The Batch (DeepLearning.AI)': 'https://www.deeplearning.ai/the-batch/rss/',

        # ── AI research lab blogs ───────────────────────────────────────────
        'HuggingFace Blog':     'https://huggingface.co/blog/feed.xml',
        'OpenAI Blog':          'https://openai.com/blog/rss.xml',
        'Anthropic Blog':       'https://www.anthropic.com/news/rss',
        'Google DeepMind':      'https://deepmind.google/blog/rss.xml',
        'Meta AI Blog':         'https://ai.meta.com/blog/rss/',
        'Mistral AI':           'https://mistral.ai/news/rss',
        'Microsoft Research':   'https://www.microsoft.com/en-us/research/feed/',

        # ── VC / industry perspective ───────────────────────────────────────
        'a16z':                 'https://a16z.com/feed/',
        'VentureBeat AI':       'https://venturebeat.com/category/ai/feed/',
    }

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            count_before = len(articles)
            for entry in feed.entries[:8]:  # max 8 per source
                if not _entry_is_fresh(entry):
                    continue
                summary = entry.get('summary', '')
                articles.append({
                    'title':     entry.title,
                    'source':    source,
                    'url':       entry.link,
                    'published': entry.get('published', ''),
                    'summary':   summary[:500] + '...' if len(summary) > 500 else summary,
                })
            added = len(articles) - count_before
            print(f"✓ {source}: {added} articles")
            time.sleep(0.5)  # polite delay between requests
        except Exception as e:
            print(f"✗ {source} error: {e}")

    return articles


def remove_duplicates(articles: List[Dict]) -> List[Dict]:
    """Deduplicate articles by URL."""
    seen_urls = set()
    unique = []
    for article in articles:
        if article['url'] not in seen_urls:
            seen_urls.add(article['url'])
            unique.append(article)
    return unique


def main():
    """Main entry point."""
    print("🤖 Starting AI news collection...")

    all_articles = fetch_ai_news_rss()
    unique_articles = remove_duplicates(all_articles)
    print(f"\n📊 Total unique articles: {len(unique_articles)}")

    # Keep the most recent 50 items
    recent_articles = unique_articles[:50]

    output_dir = os.path.join(os.path.dirname(__file__), '..', '.tmp')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'ai_news.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(recent_articles, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(recent_articles)} articles → {output_file}")
    return len(recent_articles) > 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
