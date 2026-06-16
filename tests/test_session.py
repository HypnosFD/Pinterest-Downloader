"""Tests for session and cookie loading utilities."""

import os
import tempfile
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from pinterest_downloader.session import load_cookies, get_session, create_sessions


class TestLoadCookies:
    def test_load_valid_cookie_file(self, tmp_path):
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("# Netscape HTTP Cookie File\n.pinterest.com\tTRUE\t/\tFALSE\t0\tcsrftoken\tabc123\n")
        result = load_cookies(str(cookie_file))
        assert result is not None

    def test_load_nonexistent_file(self):
        result = load_cookies("/nonexistent/cookies.txt")
        assert result is None

    def test_load_empty_cookie_file(self, tmp_path):
        cookie_file = tmp_path / "cookies.txt"
        cookie_file.write_text("")
        result = load_cookies(str(cookie_file))
        assert result is not None
        assert len(result) == 0


class TestGetSession:
    def test_create_page_session(self):
        session = get_session(0, {}, None)
        assert session is not None
        assert "User-Agent" in session.headers
        assert "text/html" in session.headers["Accept"]

    def test_create_api_session(self):
        session = get_session(1, {}, None)
        assert session is not None
        assert "X-APP-VERSION" in session.headers
        assert "X-Requested-With" in session.headers

    def test_create_image_session(self):
        session = get_session(3, {}, None)
        assert session is not None
        assert "image/webp" in session.headers["Accept"]

    def test_create_video_session(self):
        session = get_session(4, {}, None)
        assert session is not None
        assert session.headers["Accept"] == "*/*"


class TestCreateSessions:
    def test_create_all_sessions(self):
        sessions = create_sessions({}, None)
        assert "page" in sessions
        assert "feed" in sessions
        assert "image" in sessions
        assert "video" in sessions
        assert len(sessions) == 4
