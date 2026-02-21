#!/usr/bin/env python3
"""
AI Idea Analysis Script
Supports both local LLM (Ollama / LM Studio) and cloud LLM (Gemini).
Control via LLM_PROVIDER env var: 'gemini' (default) or 'local'
"""

import json
import os
from datetime import datetime
from typing import List, Dict
from dotenv import load_dotenv

try:
    load_dotenv()
except:
    pass

LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'gemini').lower()

# ──────────────────────────────────────────────
# Shared prompt builder
# ──────────────────────────────────────────────

# ──────────────────────────────────────────────
# 🌐 LANGUAGE CONFIGURATION
# ──────────────────────────────────────────────
# The response language is controlled by the prompt below (inside build_prompt).
# To change the output language, do ONE of the following:
#
#   Option A — Edit the language instruction line in the prompt:
#     Change: "모든 내용을 한국어로 작성하세요."
#     To e.g.: "Write all content in English." / "Répondez entièrement en français." etc.
#
#   Option B — Set the RESPONSE_LANGUAGE env var in your .env file:
#     RESPONSE_LANGUAGE=English
#     RESPONSE_LANGUAGE=Japanese
#     RESPONSE_LANGUAGE=Spanish
#   (The prompt will inject it automatically.)
# ──────────────────────────────────────────────

RESPONSE_LANGUAGE = os.getenv('RESPONSE_LANGUAGE', '한국어')  # default: Korean


def build_prompt(news_articles: List[Dict], social_posts: List[Dict]) -> str:
    # To change output language → set RESPONSE_LANGUAGE in your .env
    # e.g. RESPONSE_LANGUAGE=English  or  RESPONSE_LANGUAGE=日本語
    prompt = f"""당신은 AI 프로덕트 기획 전문가이자 1인 창업가 멘토입니다.
아래 최신 AI 트렌드와 뉴스를 분석하여, 즉시 실행 가능한 AI 제품 아이디어 3가지를 도출해주세요.

규칙:
- 모든 내용을 {RESPONSE_LANGUAGE}로 작성하세요.
- 구체적이고 실질적인 내용으로 작성하세요 (일반적인 내용 지양).

## 최신 AI 뉴스 ({len(news_articles)}개)
"""
    for i, article in enumerate(news_articles[:15], 1):
        prompt += f"{i}. [{article['source']}] {article['title']}\n"

    prompt += f"\n## 커뮤니티 트렌드 ({len(social_posts)}개)\n"

    for i, post in enumerate(social_posts[:15], 1):
        prompt += f"{i}. [{post['source']}] {post['title']}\n"

    prompt += f"""

JSON 형식으로만 응답하세요 — 마크다운 코드 펜스나 다른 텍스트 없이:

{{
  "executive_summary": "오늘의 주요 AI 트렌드 요약 ({RESPONSE_LANGUAGE}, 200자 이내)",
  "top_themes": ["테마 1", "테마 2", "테마 3"],
  "product_ideas": [
    {{
      "idea_name": "아이디어 이름 1",
      "description": "어떤 문제를 해결하는지, 어떻게 해결하는지 ({RESPONSE_LANGUAGE}, 150자 이내)",
      "target_users": "예상 타겟 유저 ({RESPONSE_LANGUAGE})",
      "why_now": "왜 지금 이 타이밍인지 ({RESPONSE_LANGUAGE})",
      "actionable_step_1": "오늘 당장 시작할 수 있는 첫 번째 실행 단계 ({RESPONSE_LANGUAGE})"
    }},
    {{
      "idea_name": "아이디어 이름 2",
      "description": "어떤 문제를 해결하는지, 어떻게 해결하는지 ({RESPONSE_LANGUAGE}, 150자 이내)",
      "target_users": "예상 타겟 유저 ({RESPONSE_LANGUAGE})",
      "why_now": "왜 지금 이 타이밍인지 ({RESPONSE_LANGUAGE})",
      "actionable_step_1": "오늘 당장 시작할 수 있는 첫 번째 실행 단계 ({RESPONSE_LANGUAGE})"
    }},
    {{
      "idea_name": "아이디어 이름 3",
      "description": "어떤 문제를 해결하는지, 어떻게 해결하는지 ({RESPONSE_LANGUAGE}, 150자 이내)",
      "target_users": "예상 타겟 유저 ({RESPONSE_LANGUAGE})",
      "why_now": "왜 지금 이 타이밍인지 ({RESPONSE_LANGUAGE})",
      "actionable_step_1": "오늘 당장 시작할 수 있는 첫 번째 실행 단계 ({RESPONSE_LANGUAGE})"
    }}
  ]
}}"""
    return prompt



# ──────────────────────────────────────────────
# Gemini backend
# ──────────────────────────────────────────────

def analyze_with_gemini(news_articles: List[Dict], social_posts: List[Dict]) -> Dict:
    import google.generativeai as genai

    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not set")

    genai.configure(api_key=api_key)
    model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
    model = genai.GenerativeModel(model_name)
    print(f"  provider : Gemini ({model_name})")

    response = model.generate_content(build_prompt(news_articles, social_posts))
    text = response.text.strip().lstrip('```json').lstrip('```').rstrip('```').strip()
    return json.loads(text)


# ──────────────────────────────────────────────
# Local LLM backend (Ollama / LM Studio)
# ──────────────────────────────────────────────

def analyze_with_local(news_articles: List[Dict], social_posts: List[Dict]) -> Dict:
    from openai import OpenAI

    base_url = os.getenv('LOCAL_LLM_API_BASE', 'http://localhost:1234/v1')
    api_key  = os.getenv('LOCAL_LLM_API_KEY', 'local-key')
    model    = os.getenv('LOCAL_LLM_MODEL', 'local-model')

    print(f"  provider : Local LLM ({base_url}, model={model})")

    client = OpenAI(base_url=base_url, api_key=api_key)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful AI product strategist. Output valid JSON only."},
            {"role": "user",   "content": build_prompt(news_articles, social_posts)},
        ],
        temperature=0.7,
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content.strip())


# ──────────────────────────────────────────────
# Dispatcher
# ──────────────────────────────────────────────

def analyze_ideas(news_articles: List[Dict], social_posts: List[Dict]) -> Dict:
    print(f"🤖 Starting AI analysis...")
    try:
        if LLM_PROVIDER == 'local':
            result = analyze_with_local(news_articles, social_posts)
        else:
            result = analyze_with_gemini(news_articles, social_posts)

        print(f"✓ Analysis complete — {len(result.get('product_ideas', []))} ideas generated")
        return result

    except Exception as e:
        print(f"✗ Analysis failed ({LLM_PROVIDER}): {e}")
        return {
            "executive_summary": f"Analysis failed. Check your LLM_PROVIDER='{LLM_PROVIDER}' config and API key/server.",
            "top_themes": ["Error", "Config Issue"],
            "product_ideas": []
        }


# ──────────────────────────────────────────────
# Data loader
# ──────────────────────────────────────────────

def load_data() -> Dict:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(script_dir, '..', '.tmp')

    def load(filename):
        path = os.path.join(tmp_dir, filename)
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    return {'news': load('ai_news.json'), 'social': load('ai_trends.json')}


# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────

def main():
    print(f"🤖 IdeaHunter — Analyze Ideas (provider: {LLM_PROVIDER})")

    data = load_data()
    if not data['news'] and not data['social']:
        print("❌ No data to analyze")
        return False

    print(f"✓ Loaded {len(data['news'])} news  |  {len(data['social'])} trends")

    analysis = analyze_ideas(data['news'], data['social'])

    report = {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'llm_provider': LLM_PROVIDER,
        'llm_analysis': analysis,
        'news_count': len(data['news']),
        'social_count': len(data['social']),
        'top_news': data['news'][:5],
        'top_social': data['social'][:5],
    }

    script_dir = os.path.dirname(os.path.abspath(__file__))
    tmp_dir = os.path.join(script_dir, '..', '.tmp')
    os.makedirs(tmp_dir, exist_ok=True)
    output_file = os.path.join(tmp_dir, 'llm_report.json')

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"✅ Report saved → {output_file}")
    return True


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
