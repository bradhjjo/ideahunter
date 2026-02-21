# 💡 IdeaHunter

Automated daily pipeline that collects the latest AI news and community trends, analyzes them with an LLM, and delivers **3 actionable AI product ideas** to your Telegram channel every morning.

## How It Works

```
RSS Feeds (AI news)  ──┐
GitHub Trending      ──┼──► LLM Analysis ──► Telegram Digest
Product Hunt         ──┤    (Gemini or
Reddit AI subs       ──┘     Local LLM)
```

## Features

- **Multi-source data collection** — HuggingFace Blog, OpenAI Blog, VentureBeat, Product Hunt, GitHub Trending, Reddit (r/AItools, r/MachineLearning, r/SideProject)
- **Flexible LLM backend** — Gemini (cloud, default) or any local LLM via OpenAI-compatible API (Ollama, LM Studio)
- **Language-configurable output** — Korean by default; change one env var to switch to any language
- **Daily Telegram delivery** — formatted HTML digest with trend summary + top 3 ideas
- **Zero hardcoded secrets** — all credentials loaded from environment variables

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/bradhjjo/ideahunter.git
cd ideahunter
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Edit .env with your credentials
```

Minimum required variables:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GEMINI_API_KEY=your_gemini_api_key   # if using Gemini (default)
```

### 3. Run

```bash
python execution/main.py
```

### 4. Schedule (daily automation)

```bash
python execution/scheduler.py
```

Or set `SCHEDULE_TIME=07:00` in `.env` and keep the scheduler process running.

## LLM Provider Options

Set `LLM_PROVIDER` in `.env`:

| Value | Description |
|-------|-------------|
| `gemini` (default) | Google Gemini API — requires `GEMINI_API_KEY` |
| `local` | Local LLM via OpenAI-compatible API (Ollama / LM Studio) |

For local LLM, also set:

```env
LLM_PROVIDER=local
LOCAL_LLM_API_BASE=http://localhost:11434/v1   # Ollama
LOCAL_LLM_MODEL=llama3
```

## Output Language

Default output language is **Korean**. To change it:

```env
RESPONSE_LANGUAGE=English    # or: 日本語, Español, Français, etc.
```

## Project Structure

```
execution/
├── main.py                  # Pipeline orchestrator
├── fetch_news_rss.py        # AI news from RSS feeds
├── fetch_trends.py          # GitHub / Product Hunt / Reddit trends
├── analyze_ideas.py         # LLM analysis — Gemini or local
├── send_telegram_message.py # Telegram delivery
└── scheduler.py             # Daily cron-style scheduler
```

## GitHub Actions (Cloud Deployment)

Push to GitHub, then add your secrets under **Settings → Secrets and variables → Actions**:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GEMINI_API_KEY`

See [`GITHUB_ACTIONS_SETUP.md`](GITHUB_ACTIONS_SETUP.md) for the full workflow file.

## License

MIT
