"""Tests for the JSON fence-stripping helper in analyze_ideas."""

import unittest

from tests import conftest  # noqa: F401 — installs stubs and sys.path

from analyze_ideas import _parse_json_response


class ParseJsonResponseTests(unittest.TestCase):
    def test_plain_json_passthrough(self):
        self.assertEqual(_parse_json_response('{"a": 1}'), {"a": 1})

    def test_strips_json_fence(self):
        self.assertEqual(
            _parse_json_response('```json\n{"a": 1}\n```'),
            {"a": 1},
        )

    def test_strips_bare_fence(self):
        self.assertEqual(
            _parse_json_response('```\n{"a": 1}\n```'),
            {"a": 1},
        )

    def test_tolerates_surrounding_whitespace(self):
        self.assertEqual(
            _parse_json_response('   ```json   {"a": 1}   ```   '),
            {"a": 1},
        )

    def test_preserves_json_content_with_word_json_inside(self):
        # Regression test for the lstrip('```json') bug: lstrip treats its
        # argument as a character set, so it used to chew off letters like
        # 'j', 'o', 'n' from JSON content that happened to begin with them.
        payload = '{"name": "json-rpc", "ok": true}'
        self.assertEqual(
            _parse_json_response(payload),
            {"name": "json-rpc", "ok": True},
        )


if __name__ == "__main__":
    unittest.main()
