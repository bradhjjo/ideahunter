#!/usr/bin/env python3
"""
AI News RSS Fetcher.
Collects articles from major AI news/blog RSS feeds and saves them to .tmp/ai_news.json.

To add more sources, append entries to the `feeds` dict inside fetch_ai_news_rss().
"""

import feedparser
import json
import os
from typing import List, Dict
import time


def fetch_ai_news_rss() -> List[Dict]:
    """Fetch articles from AI news/newsletter RSS feeds.

    Some newsletters don't offer RSS, so we use equivalent blog/publication feeds.
    Add or remove sources in the dict below as needed.
    """
    articles = []

    feeds = {
        'HuggingFace Blog': 'https://huggingface.co/blog/feed.xml',
        'OpenAI Blog':      'https://openai.com/blog/rss.xml',
        'VentureBeat AI':   'https://venturebeat.com/category/ai/feed/',
    }

    for source, url in feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:  # max 10 per source
                summary = entry.get('summary', '')
                articles.append({
                    'title':     entry.title,
                    'source':    source,
                    'url':       entry.link,
                    'published': entry.get('published', ''),
                    'summary':   summary[:500] + '...' if len(summary) > 500 else summary,
                })
            count = len([a for a in articles if a['source'] == source])
            print(f"✓ {source}: {count} articles")
            time.sleep(1)  # polite delay between requests
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

    # Keep the most recent 30 items (feeds are already newest-first)
    recent_articles = unique_articles[:30]

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
