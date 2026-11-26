"""Tests for the AI keyword regex used by every trend fetcher."""

import unittest

from tests import conftest  # noqa: F401

from fetch_trends import AI_KEYWORD_PATTERN


class AiKeywordPatternTests(unittest.TestCase):
    def test_matches_real_ai_terms(self):
        for text in [
            "New LLM agent released",
            "Open-source AI tool",
            "Diffusion model for video",
            "Retrieval-augmented generation (RAG) tutorial",
            "ML pipelines at scale",
        ]:
            with self.subTest(text=text):
                self.assertIsNotNone(AI_KEYWORD_PATTERN.search(text))

    def test_avoids_substring_false_positives(self):
        # Regression test: a plain `'ai' in text.lower()` check used to
        # match "said", "main", "waiting" → polluted the trend stream.
        for text in [
            "He said hello in main thread",
            "Waiting for results",
            "Maintain backwards compatibility",
            "I am ai-curious",  # tokenises into "ai-curious" → still matches
        ]:
            with self.subTest(text=text):
                if "ai-" in text or text.endswith("ai"):
                    continue
                self.assertIsNone(AI_KEYWORD_PATTERN.search(text), text)


if __name__ == "__main__":
    unittest.main()
