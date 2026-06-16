"""Tests for the config module."""

import pytest
from pinterest_downloader.config import (
    IS_WIN,
    WIN_MAX_PATH,
    RETRY_TIMEOUTS,
    RETRY_SLEEP_SECONDS,
    PAGE_SIZE,
    PINTEREST_BASE_URL,
    MEDIA_EXTENSIONS,
    X_TAG,
    DONE_TAG,
    PLUS_TAG,
)


class TestConfig:
    def test_win_max_path(self):
        assert WIN_MAX_PATH == 255

    def test_retry_timeout(self):
        assert RETRY_TIMEOUTS == (15, 30, 40, 50, 60)
        assert len(RETRY_TIMEOUTS) == 5
        assert all(isinstance(t, int) for t in RETRY_TIMEOUTS)
        assert all(t > 0 for t in RETRY_TIMEOUTS)

    def test_retry_sleep(self):
        assert RETRY_SLEEP_SECONDS == 5

    def test_page_size(self):
        assert PAGE_SIZE == 25

    def test_pinterest_base_url(self):
        assert PINTEREST_BASE_URL.startswith("https://")
        assert "pinterest" in PINTEREST_BASE_URL

    def test_media_extensions(self):
        assert ".jpg" in MEDIA_EXTENSIONS
        assert ".png" in MEDIA_EXTENSIONS
        assert ".mp4" in MEDIA_EXTENSIONS
        assert ".gif" in MEDIA_EXTENSIONS
        assert all(ext.startswith(".") for ext in MEDIA_EXTENSIONS)

    def test_ui_symbols(self):
        assert isinstance(X_TAG, str)
        assert isinstance(DONE_TAG, str)
        assert isinstance(PLUS_TAG, str)
        assert len(X_TAG) > 0
