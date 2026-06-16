"""Tests for the sanitize function and path utilities."""

import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from pinterest_downloader.paths import sanitize


class TestSanitize:
    def test_normal_string(self):
        assert sanitize("hello world") == "hello world"

    def test_strip_whitespace(self):
        assert sanitize("  hello  ") == "hello"

    def test_multiple_spaces(self):
        assert sanitize("hello   world") == "hello world"

    def test_remove_angle_brackets(self):
        assert sanitize("hello<world>") == "helloworld"

    def test_remove_question_marks(self):
        assert sanitize("hello?world") == "helloworld"

    def test_remove_asterisks(self):
        assert sanitize("hello*world") == "helloworld"

    def test_replace_slashes(self):
        assert sanitize("hello/world") == "hello_world"

    def test_replace_backslashes(self):
        assert sanitize("hello\\world") == "hello_world"

    def test_replace_pipes(self):
        assert sanitize("hello|world") == "hello_world"

    def test_replace_colons(self):
        assert sanitize("hello:world") == "hello_world"

    def test_replace_dots(self):
        assert sanitize("hello.world") == "hello_world"

    def test_replace_quotes(self):
        assert sanitize('hello"world') == "hello'world"

    def test_empty_string(self):
        assert sanitize("") == ""

    def test_only_special_chars(self):
        assert sanitize("?*<>") == ""

    def test_unicode(self):
        result = sanitize("hello 你好")
        assert result == "hello 你好"

    def test_complex_path(self):
        result = sanitize("My Board: Section <v2>?")
        assert "<" not in result
        assert ">" not in result
        assert "?" not in result
        assert ":" not in result
        assert "  " not in result
