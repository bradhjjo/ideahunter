"""Tests for the Telegram message splitter and provider label."""

import os
import unittest

from tests import conftest  # noqa: F401

from send_telegram_message import (
    _provider_label,
    format_llm_report,
    split_for_telegram,
)


def _sample_report() -> dict:
    return {
        "date": "2026-05-12",
        "llm_provider": "local",
        "news_count": 10,
        "social_count": 5,
        "llm_analysis": {
            "executive_summary": "x" * 200,
            "top_themes": ["agents", "rag", "video"],
            "product_ideas": [
                {
                    "idea_name": f"Idea {i}",
                    "description": "d" * 200,
                    "target_users": "indie hackers",
                    "why_now": "the model just shipped",
                    "actionable_step_1": "ship a prototype today",
                }
                for i in range(5)
            ],
        },
    }


class SplitForTelegramTests(unittest.TestCase):
    def test_short_message_returns_single_chunk(self):
        self.assertEqual(split_for_telegram("hi\nthere", limit=4096), ["hi\nthere"])

    def test_long_message_splits_under_limit(self):
        msg = format_llm_report(_sample_report())
        chunks = split_for_telegram(msg, limit=400)
        self.assertGreater(len(chunks), 1)
        for c in chunks:
            self.assertLessEqual(len(c), 400)

    def test_split_preserves_content(self):
        msg = format_llm_report(_sample_report())
        chunks = split_for_telegram(msg, limit=400)
        # Joining on '\n' (the split boundary) round-trips the content modulo
        # the inter-chunk newlines we intentionally drop.
        self.assertEqual(
            "\n".join(chunks).replace("\n", ""),
            msg.replace("\n", ""),
        )

    def test_split_keeps_html_tags_balanced(self):
        msg = format_llm_report(_sample_report())
        for chunk in split_for_telegram(msg, limit=400):
            self.assertEqual(chunk.count("<b>"), chunk.count("</b>"), chunk)
            self.assertEqual(chunk.count("<i>"), chunk.count("</i>"), chunk)


class ProviderLabelTests(unittest.TestCase):
    def test_gemini_label_includes_model(self):
        os.environ["GEMINI_MODEL"] = "gemini-2.5-flash"
        label = _provider_label({"llm_provider": "gemini"})
        self.assertIn("Gemini", label)
        self.assertIn("gemini-2.5-flash", label)

    def test_local_label_includes_model(self):
        os.environ["LOCAL_LLM_MODEL"] = "llama3"
        label = _provider_label({"llm_provider": "local"})
        self.assertIn("Local LLM", label)
        self.assertIn("llama3", label)

    def test_unknown_provider_falls_back(self):
        self.assertEqual(_provider_label({"llm_provider": ""}), "LLM")


if __name__ == "__main__":
    unittest.main()
