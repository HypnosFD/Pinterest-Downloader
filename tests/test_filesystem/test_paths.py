"""Tests for the sanitize function and path utilities."""

import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from pinterest_downloader.paths import sanitize, sanitize_fname


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


class TestSanitizeFname:
    def test_strips_cyrillic(self):
        result = sanitize_fname("_Скетч сложный ракурс_Скетч рисунки")
        assert result == ""

    def test_strips_emoji(self):
        result = sanitize_fname("Red Armored Lady Knight✨")
        assert "✨" not in result
        assert result == "Red Armored Lady Knight"

    def test_limits_length(self):
        long_name = "a" * 200
        result = sanitize_fname(long_name)
        assert len(result) <= 80

    def test_collapses_whitespace(self):
        result = sanitize_fname("hello   world")
        assert result == "hello world"

    def test_strips_special_chars(self):
        result = sanitize_fname("hello world & @ # % ! ~")
        assert "&" not in result
        assert "@" not in result
        assert "#" not in result
        assert "%" not in result
        assert "!" not in result
        assert "~" not in result
        assert "and" in result

    def test_replaces_ampersand(self):
        result = sanitize_fname("Tom & Jerry")
        assert result == "Tom and Jerry"

    def test_mixed_ascii_and_non_ascii(self):
        result = sanitize_fname("Knight armored✨ леди")
        assert result == "Knight armored"
        assert "леди" not in result

    def test_empty_after_strip(self):
        result = sanitize_fname("✨✨✨")
        assert result == ""

    def test_normal_ascii_preserved(self):
        result = sanitize_fname("Simple Sketch Drawing")
        assert result == "Simple Sketch Drawing"

    def test_strips_brackets(self):
        result = sanitize_fname("photo [draft] (v2)")
        assert result == "photo draft v2"

    def test_underscores_as_separators(self):
        result = sanitize_fname("_title_desc_more_Sketch_Fashion")
        assert "__" not in result
        assert result == "title desc more Sketch Fashion"

    def test_cyrillic_with_underscores(self):
        result = sanitize_fname("_Скетч сложный_Скетч рисунки_Sketch_Fashion")
        assert result == "Sketch Fashion"

    def test_real_world_example(self):
        result = sanitize_fname("_Red Armored Lady Knight_✨ This image showcases a knight_")
        assert result == "Red Armored Lady Knight This image showcases a knight"
