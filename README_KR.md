# 💡 IdeaHunter

매일 아침 최신 AI 뉴스와 커뮤니티 트렌드를 자동으로 수집·분석해 **실행 가능한 AI 제품 아이디어 5개**를 텔레그램으로 보내주는 파이프라인입니다.

## 동작 방식

```
RSS 피드 (AI 뉴스 + 연구소 + VC) ─┐
GitHub Trending (AI 레포)         │
Product Hunt (AI 제품)            │
Reddit (AI 서브레딧)              ├──► LLM 분석 ──► 텔레그램 다이제스트
Hacker News + YC Launches         │    (Gemini 또는
Papers With Code                  │     로컬 LLM)
BetaList / Indie Hackers          ─┘
```

## 주요 기능

- **다중 소스 수집** — 13개의 AI 뉴스/블로그 RSS (TLDR AI, Ben's Bites, Import AI, The Batch, HuggingFace, OpenAI, Anthropic, DeepMind, Meta AI, Mistral, Microsoft Research, a16z, VentureBeat) + 8개의 트렌드 소스 (GitHub Trending, Product Hunt, Reddit, Hacker News, YC Launches, Papers With Code, BetaList, Indie Hackers)
- **LLM 백엔드 선택** — Gemini(기본, 클라우드) 또는 OpenAI 호환 API를 지원하는 로컬 LLM (Ollama, LM Studio)
- **출력 언어 설정** — 기본은 한국어. 환경변수 한 줄로 임의 언어 전환 가능
- **텔레그램 자동 발송** — 트렌드 요약 + 아이디어 5개를 HTML로 포맷팅. 4096자 초과 시 줄 단위로 분할 전송
- **시크릿 하드코딩 없음** — 모든 인증값은 환경변수에서 로드

## 빠른 시작

### 1. 클론 & 설치

```bash
git clone https://github.com/bradhjjo/ideahunter.git
cd ideahunter
pip install -r requirements.txt
```

### 2. 환경 설정

```bash
cp .env.example .env
# .env 파일을 열어 본인 토큰/키 입력
```

필수 변수:

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
GEMINI_API_KEY=your_gemini_api_key   # Gemini 사용 시 (기본)
```

### 3. 실행

```bash
python execution/main.py
```

### 4. 자동 스케줄링

로컬에서 매일 실행하려면:

```bash
python execution/scheduler.py
```

`.env`에 `SCHEDULE_TIME=07:00`을 두고 스케줄러 프로세스를 살려두면 됩니다.

## LLM 공급자

`.env`의 `LLM_PROVIDER`로 결정:

| 값 | 설명 |
|---|---|
| `gemini` (기본) | Google Gemini API — `GEMINI_API_KEY` 필요 |
| `local` | OpenAI 호환 API의 로컬 LLM (Ollama / LM Studio) |

로컬 LLM 사용 시 추가 설정:

```env
LLM_PROVIDER=local
LOCAL_LLM_API_BASE=http://localhost:11434/v1   # Ollama
LOCAL_LLM_MODEL=llama3
```

## 출력 언어

기본 한국어. 변경하려면:

```env
RESPONSE_LANGUAGE=English    # 또는 日本語, Español, Français 등
```

## 프로젝트 구조

```
execution/
├── main.py                  # 파이프라인 오케스트레이터
├── fetch_news_rss.py        # AI 뉴스 RSS 수집
├── fetch_trends.py          # GitHub / Product Hunt / Reddit / HN / YC / PwC / BetaList / IH
├── analyze_ideas.py         # LLM 분석 (Gemini / 로컬)
├── send_telegram_message.py # 텔레그램 발송 (4096자 분할)
└── scheduler.py             # 로컬 cron 스케줄러
```

## GitHub Actions (클라우드 배포)

리포지토리에 푸시한 뒤, **Settings → Secrets and variables → Actions**에 다음 시크릿을 추가:

- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `GEMINI_API_KEY`

상세 설정은 [`GITHUB_ACTIONS_SETUP.md`](GITHUB_ACTIONS_SETUP.md) 참고.

## 라이선스

MIT
