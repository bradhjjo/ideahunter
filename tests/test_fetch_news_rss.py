"""Tests for the freshness filter on news RSS entries."""

import calendar
import time
import unittest

from tests import conftest  # noqa: F401

from fetch_news_rss import _entry_is_fresh


def _struct_offset(seconds_ago: int):
    return time.gmtime(calendar.timegm(time.gmtime()) - seconds_ago)


class EntryIsFreshTests(unittest.TestCase):
    def test_recent_entry_is_kept(self):
        self.assertTrue(_entry_is_fresh({"published_parsed": _struct_offset(300)}))

    def test_old_entry_is_dropped(self):
        # 60 days old, default window is 7 days.
        self.assertFalse(
            _entry_is_fresh({"published_parsed": _struct_offset(60 * 86400)})
        )

    def test_updated_parsed_is_also_consulted(self):
        self.assertFalse(
            _entry_is_fresh({"updated_parsed": _struct_offset(60 * 86400)})
        )

    def test_entry_without_date_is_kept(self):
        self.assertTrue(_entry_is_fresh({}))

    def test_custom_window(self):
        # 10-day-old entry: stale at 7 days, fresh at 30.
        struct = _struct_offset(10 * 86400)
        self.assertFalse(_entry_is_fresh({"published_parsed": struct}, max_age_days=7))
        self.assertTrue(_entry_is_fresh({"published_parsed": struct}, max_age_days=30))


if __name__ == "__main__":
    unittest.main()
