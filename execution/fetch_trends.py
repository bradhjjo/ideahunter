#!/usr/bin/env python3
"""
AI Trends Fetcher.
Collects trending AI items from multiple community and discovery platforms.
Results are saved to .tmp/ai_trends.json.

Sources:
  - GitHub Trending (AI/ML repos)
  - Product Hunt (AI products)
  - Reddit AI subreddits
  - Hacker News (AI-filtered)
  - Y Combinator Launches
  - Papers With Code (trending papers)
  - BetaList (early-stage AI startups)
  - Indie Hackers
"""

import os
import json
import requests
from typing import List, Dict
import feedparser
import time


# ──────────────────────────────────────────────
# GitHub Trending
# ──────────────────────────────────────────────

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
            ai_keywords = ['ai', 'ml', 'llm', 'gpt', 'model', 'agent', 'rag', 'diffusion', 'transformer']

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


# ──────────────────────────────────────────────
# Product Hunt
# ──────────────────────────────────────────────

def fetch_producthunt_rss() -> List[Dict]:
    """Fetch new AI products from Product Hunt RSS feed."""
    url = "https://www.producthunt.com/feed"
    products = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            title   = entry.title.lower()
            summary = entry.get('summary', '').lower()
            if any(kw in title or kw in summary for kw in ['ai', 'gpt', 'intelligent', 'agent', 'llm', 'ml']):
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


# ──────────────────────────────────────────────
# Reddit
# ──────────────────────────────────────────────

def fetch_reddit_ai() -> List[Dict]:
    """Fetch hot posts from AI-related subreddits via the Reddit JSON API."""
    subreddits = ['AItools', 'SideProject', 'MachineLearning', 'LocalLLaMA', 'artificial']
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

                    # For general subs, only keep AI-related posts
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
            time.sleep(1)
        except Exception as e:
            print(f"✗ Reddit r/{sub} error: {e}")

    return posts


# ──────────────────────────────────────────────
# Hacker News
# ──────────────────────────────────────────────

def fetch_hackernews() -> List[Dict]:
    """Fetch AI-related posts from Hacker News via HNRSS filtered feeds.

    Uses free HNRSS.org feeds — no auth required.
    To change keywords, edit the `hn_feeds` dict below.
    """
    hn_feeds = {
        'HN (AI/LLM)':   'https://hnrss.org/newest?q=AI+LLM&points=10',
        'HN (Show HN)':  'https://hnrss.org/show?points=10',
        'HN (Ask HN)':   'https://hnrss.org/ask?points=5',
    }
    posts = []
    ai_keywords = ['ai', 'llm', 'gpt', 'model', 'agent', 'ml', 'machine learning', 'generative']

    for source, url in hn_feeds.items():
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:10]:
                title = entry.title.lower()
                # For Show/Ask HN, filter to AI-related only
                if 'show' in source.lower() or 'ask' in source.lower():
                    if not any(kw in title for kw in ai_keywords):
                        continue
                posts.append({
                    'title':       entry.title,
                    'url':         entry.link,
                    'description': entry.get('summary', '')[:300],
                    'source':      source,
                })
            print(f"✓ {source}: {len([p for p in posts if p['source'] == source])} posts")
            time.sleep(0.5)
        except Exception as e:
            print(f"✗ {source} error: {e}")

    return posts


# ──────────────────────────────────────────────
# Y Combinator Launches
# ──────────────────────────────────────────────

def fetch_yc_launches() -> List[Dict]:
    """Fetch YC batch launch posts from Hacker News launches RSS.

    These are 'Launch HN' posts — strong signal for hot new startups.
    """
    url = "https://hnrss.org/launches"
    launches = []
    ai_keywords = ['ai', 'llm', 'gpt', 'ml', 'model', 'agent', 'data', 'automation', 'copilot']

    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            title   = entry.title.lower()
            summary = entry.get('summary', '').lower()
            if any(kw in title or kw in summary for kw in ai_keywords):
                launches.append({
                    'title':       entry.title,
                    'url':         entry.link,
                    'description': entry.get('summary', '')[:400],
                    'source':      'YC Launches (HN)',
                })
        print(f"✓ YC Launches (AI): {len(launches)} items")
    except Exception as e:
        print(f"✗ YC Launches error: {e}")

    return launches


# ──────────────────────────────────────────────
# Papers With Code
# ──────────────────────────────────────────────

def fetch_papers_with_code() -> List[Dict]:
    """Fetch trending AI papers from the Papers With Code public API.

    Free, no API key required. Returns papers with GitHub repos attached.
    """
    url = "https://paperswithcode.com/api/v1/papers/?ordering=-published&has_code=true&page_size=10"
    papers = []

    try:
        resp = requests.get(url, timeout=10, headers={'User-Agent': 'IdeaHunterBot/1.0'})
        if resp.status_code == 200:
            results = resp.json().get('results', [])
            for paper in results:
                papers.append({
                    'title':       paper.get('title', ''),
                    'url':         f"https://paperswithcode.com{paper.get('url', '')}",
                    'description': paper.get('abstract', '')[:400],
                    'source':      'Papers With Code',
                })
        print(f"✓ Papers With Code: {len(papers)} papers")
    except Exception as e:
        print(f"✗ Papers With Code error: {e}")

    return papers


# ──────────────────────────────────────────────
# BetaList
# ──────────────────────────────────────────────

def fetch_betalist() -> List[Dict]:
    """Fetch early-stage AI startups from BetaList RSS."""
    url = "https://betalist.com/feed"
    startups = []
    ai_keywords = ['ai', 'llm', 'gpt', 'machine learning', 'generative', 'automation', 'agent']

    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:20]:
            title   = entry.title.lower()
            summary = entry.get('summary', '').lower()
            if any(kw in title or kw in summary for kw in ai_keywords):
                startups.append({
                    'title':       entry.title,
                    'url':         entry.link,
                    'description': entry.get('summary', '')[:400],
                    'source':      'BetaList (AI)',
                })
        print(f"✓ BetaList AI: {len(startups)} startups")
    except Exception as e:
        print(f"✗ BetaList error: {e}")

    return startups


# ──────────────────────────────────────────────
# Indie Hackers
# ──────────────────────────────────────────────

def fetch_indiehackers() -> List[Dict]:
    """Fetch posts from Indie Hackers RSS feed (builder sentiment + side projects)."""
    url = "https://www.indiehackers.com/feed.xml"
    posts = []
    ai_keywords = ['ai', 'llm', 'gpt', 'automation', 'saas', 'product', 'launch']

    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:
            title   = entry.title.lower()
            summary = entry.get('summary', entry.get('description', '')).lower()
            if any(kw in title or kw in summary for kw in ai_keywords):
                posts.append({
                    'title':       entry.title,
                    'url':         entry.link,
                    'description': entry.get('summary', entry.get('description', ''))[:300],
                    'source':      'Indie Hackers',
                })
        print(f"✓ Indie Hackers: {len(posts)} posts")
    except Exception as e:
        print(f"✗ Indie Hackers error: {e}")

    return posts


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    """Main entry point."""
    print("🚀 Starting AI trends collection...")

    all_trends: List[Dict] = []

    all_trends.extend(fetch_github_trending())
    all_trends.extend(fetch_producthunt_rss())
    all_trends.extend(fetch_reddit_ai())
    all_trends.extend(fetch_hackernews())
    all_trends.extend(fetch_yc_launches())
    all_trends.extend(fetch_papers_with_code())
    all_trends.extend(fetch_betalist())
    all_trends.extend(fetch_indiehackers())

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
