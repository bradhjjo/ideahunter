#!/usr/bin/env python3
"""
AI Trends Fetcher.
Collects trending AI items from GitHub, Product Hunt, and Reddit.
Results are saved to .tmp/ai_trends.json.
"""

import os
import json
import requests
from typing import List, Dict
import feedparser
import time


def fetch_github_trending() -> List[Dict]:
    """Fetch trending AI/ML repositories from GitHub Trending API.

    Uses an unofficial trending API. If it goes down, replace with
    a direct scrape of github.com/trending or a self-hosted RSSHub feed.
    """
    url = "https://msh-gh-trending-api.herokuapp.com/repositories?since=daily"
    trends = []

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            repos = response.json()
            ai_keywords = ['ai', 'ml', 'llm', 'gpt', 'model', 'agent', 'rag']

            for repo in repos:
                desc = str(repo.get('description', '')).lower()
                name = str(repo.get('name', '')).lower()

                if any(kw in desc or kw in name for kw in ai_keywords):
                    trends.append({
                        'title':       f"{repo.get('author')}/{repo.get('name')}",
                        'url':         repo.get('url'),
                        'description': repo.get('description', ''),
                        'source':      'GitHub Trending (AI)',
                    })
                    if len(trends) >= 10:
                        break
    except Exception as e:
        print(f"✗ GitHub Trending error: {e}")

    print(f"✓ GitHub Trending AI: {len(trends)} items")
    return trends


def fetch_producthunt_rss() -> List[Dict]:
    """Fetch new AI products from Product Hunt RSS feed."""
    url = "https://www.producthunt.com/feed"
    products = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            title   = entry.title.lower()
            summary = entry.get('summary', '').lower()
            # Simple AI-relevance filter
            if any(kw in title or kw in summary for kw in ['ai', 'gpt', 'intelligent', 'agent', 'llm']):
                products.append({
                    'title':       entry.title,
                    'url':         entry.link,
                    'description': entry.get('summary', '')[:500],
                    'source':      'Product Hunt (AI)',
                })
        print(f"✓ Product Hunt AI: {len(products)} products")
    except Exception as e:
        print(f"✗ Product Hunt error: {e}")

    return products


def fetch_reddit_ai() -> List[Dict]:
    """Fetch hot posts from AI-related subreddits via the Reddit JSON API."""
    subreddits = ['AItools', 'SideProject', 'MachineLearning']
    posts = []
    headers = {'User-Agent': 'Mozilla/5.0 IdeaHunterBot/1.0'}

    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=10"
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                children = resp.json().get('data', {}).get('children', [])
                for item in children:
                    post = item['data']
                    if post.get('stickied') or post.get('is_video'):
                        continue
                    title = post.get('title', '')
                    text  = post.get('selftext', '')[:300]

                    # For r/SideProject, only keep AI-related posts
                    if sub == 'SideProject' and 'ai' not in title.lower() and 'ai' not in text.lower():
                        continue

                    posts.append({
                        'title':       f"[r/{sub}] {title}",
                        'url':         f"https://reddit.com{post.get('permalink')}",
                        'description': text,
                        'source':      f"Reddit (r/{sub})",
                    })
            source_count = len([p for p in posts if p['source'] == f"Reddit (r/{sub})"])
            print(f"✓ Reddit r/{sub}: {source_count} posts")
        except Exception as e:
            print(f"✗ Reddit r/{sub} error: {e}")

    return posts


def main():
    """Main entry point."""
    print("🚀 Starting AI trends collection...")

    all_trends: List[Dict] = []
    all_trends.extend(fetch_github_trending())
    all_trends.extend(fetch_producthunt_rss())
    all_trends.extend(fetch_reddit_ai())

    print(f"\n📊 Total collected trends: {len(all_trends)}")

    output_dir = os.path.join(os.path.dirname(__file__), '..', '.tmp')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, 'ai_trends.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_trends, f, ensure_ascii=False, indent=2)

    print(f"✅ Saved {len(all_trends)} trends → {output_file}")
    return len(all_trends) > 0


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
