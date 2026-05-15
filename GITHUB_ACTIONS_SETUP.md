# GitHub Actions 배포 가이드

IdeaHunter를 로컬 머신 없이 GitHub Actions에서 돌리는 방법입니다.

---

## 1. 리포지토리 푸시

```bash
git init
git add .
git commit -m "Initial commit: IdeaHunter"
git remote add origin https://github.com/YOUR_USERNAME/ideahunter.git
git push -u origin main
```

`.env` 파일은 `.gitignore`에 의해 자동 제외됩니다.

---

## 2. GitHub Secrets 등록

리포지토리 페이지 → `Settings` → `Secrets and variables` → `Actions` → `New repository secret`.

다음 3개를 등록:

| Secret 이름 | 값 |
|---|---|
| `TELEGRAM_BOT_TOKEN` | BotFather에서 발급받은 토큰 |
| `TELEGRAM_CHAT_ID` | 본인의 Chat ID (또는 채널 ID) |
| `GEMINI_API_KEY` | Google AI Studio에서 발급받은 키 |

로컬 LLM을 쓰려면 위 키 대신 `LLM_PROVIDER`, `LOCAL_LLM_API_BASE`, `LOCAL_LLM_MODEL`을 Secrets로 등록하고 워크플로의 `env:` 블록에 추가하세요. (다만 GitHub Actions 러너에서 로컬 LLM에 접근하려면 별도 터널/엔드포인트가 필요합니다.)

---

## 3. 워크플로 실행

워크플로 파일은 [`.github/workflows/daily-news.yml`](.github/workflows/daily-news.yml)에 있습니다.

### 수동 실행

`Actions` 탭 → `Daily IdeaHunter` → `Run workflow` 버튼.

### 매일 자동 실행

기본 워크플로는 `workflow_dispatch:`(수동)만 설정되어 있습니다. 매일 자동 실행하려면 `on:` 블록에 `schedule:`을 추가:

```yaml
on:
  workflow_dispatch:
  schedule:
    - cron: '0 13 * * *'   # 매일 UTC 13:00 = 한국 22:00 = CST 07:00
```

> GitHub Actions cron은 **UTC 기준**입니다.

| 원하는 현지 시간 | UTC cron 예시 (KST=UTC+9 기준) |
|---|---|
| 한국 07:00 | `0 22 * * *` (전날 UTC) |
| 한국 09:00 | `0 0 * * *` |
| 한국 21:00 | `0 12 * * *` |

> GitHub Actions 스케줄은 러너 혼잡도에 따라 수 분~수십 분 지연될 수 있습니다 (보장되는 정시 실행이 아님).

---

## 4. 실행 확인 / 디버깅

- `Actions` 탭에서 실행 로그를 확인할 수 있습니다.
- 실패 시 워크플로가 `.tmp/` 디렉터리를 `error-logs` 아티팩트로 업로드하므로 7일간 다운로드 가능합니다.
- 실패하면 GitHub가 등록된 이메일로 자동 알림을 보냅니다 (`Settings → Notifications → Actions`).

---

## 5. 비용

- GitHub Actions: 퍼블릭 리포는 무료, 프라이빗은 월 2,000분 무료 제공.
- 1회 실행에 약 1~2분 → 매일 돌려도 월 30~60분.

---

## 6. 시크릿 관리

자세한 가이드는 [`SECURITY.md`](SECURITY.md) 참고.

- `.env`는 절대 커밋 금지 (`.gitignore`에 등록되어 있음).
- 토큰이 노출되면 즉시 발급처에서 회수(revoke)하고 새 토큰으로 GitHub Secret을 갱신.
