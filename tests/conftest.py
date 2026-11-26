"""
Test bootstrap: stub the optional external dependencies (feedparser,
python-telegram-bot, google-generativeai, dotenv) so unit tests can import
the execution modules without installing the full requirements.

unittest discovers conftest.py via the regular import system if it's on the
path, but pytest will also pick it up automatically. We trigger the stubbing
at import time so it runs before any test module imports an execution module.
"""

import os
import sys
import types


def _install_stubs() -> None:
    if "feedparser" not in sys.modules:
        sys.modules["feedparser"] = types.SimpleNamespace(
            parse=lambda *a, **kw: types.SimpleNamespace(entries=[])
        )

    if "telegram" not in sys.modules:
        telegram_mod = types.ModuleType("telegram")

        class _FakeBot:
            def __init__(self, *a, **kw): pass
            async def send_message(self, **kw): return None

        telegram_mod.Bot = _FakeBot
        sys.modules["telegram"] = telegram_mod

        constants = types.ModuleType("telegram.constants")
        constants.ParseMode = types.SimpleNamespace(HTML="HTML")
        sys.modules["telegram.constants"] = constants

        error = types.ModuleType("telegram.error")
        class _TelegramError(Exception): pass
        error.TelegramError = _TelegramError
        sys.modules["telegram.error"] = error

    if "dotenv" not in sys.modules:
        dotenv = types.ModuleType("dotenv")
        dotenv.load_dotenv = lambda *a, **kw: None
        sys.modules["dotenv"] = dotenv


_install_stubs()

# Make execution/ importable as top-level modules.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXEC_DIR = os.path.join(ROOT, "execution")
if EXEC_DIR not in sys.path:
    sys.path.insert(0, EXEC_DIR)
