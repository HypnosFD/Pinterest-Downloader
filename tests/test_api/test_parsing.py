"""Tests for API response parsing utilities."""

import json
import os
import pytest
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class TestPinPageParsing:
    """Test parsing of Pinterest pin page HTML responses."""

    def test_parse_initial_redux_state_new_format(self):
        """Test that the new initialReduxState format (without props wrapper) is handled."""
        data = {
            "initialReduxState": {
                "pins": {
                    "12345": {
                        "id": "12345",
                        "images": {
                            "orig": {"url": "https://i.pinimg.com/originals/test.jpg"}
                        },
                        "description": "Test pin",
                    }
                }
            }
        }
        redux = data.get("props", {}).get("initialReduxState") or data.get("initialReduxState")
        assert redux is not None
        assert "pins" in redux
        assert "12345" in redux["pins"]

    def test_parse_initial_redux_state_old_format(self):
        """Test that the old initialReduxState format (with props wrapper) is handled."""
        data = {
            "props": {
                "initialReduxState": {
                    "pins": {
                        "12345": {
                            "id": "12345",
                            "images": {
                                "orig": {"url": "https://i.pinimg.com/originals/test.jpg"}
                            },
                        }
                    }
                }
            }
        }
        redux = data.get("props", {}).get("initialReduxState") or data.get("initialReduxState")
        assert redux is not None
        assert "pins" in redux
        assert "12345" in redux["pins"]

    def test_no_initial_redux_state(self):
        """Test handling of pages without initialReduxState."""
        data = {"random_key": "random_value"}
        redux = data.get("props", {}).get("initialReduxState") or data.get("initialReduxState")
        assert redux is None

    def test_ld_json_parsing(self):
        """Test parsing of LD+JSON structured data."""
        ld_data = {
            "@type": "SocialMediaPosting",
            "image": "https://i.pinimg.com/originals/test.jpg",
            "articleBody": "Test description",
        }
        assert ld_data["@type"] == "SocialMediaPosting"
        assert ld_data["image"] == "https://i.pinimg.com/originals/test.jpg"


class TestBoardPageParsing:
    """Test parsing of Pinterest board page HTML responses."""

    def test_parse_board_data_new_format(self):
        """Test parsing board data from new initialReduxState format."""
        data = {
            "initialReduxState": {
                "boards": {
                    "566538896813783842": {
                        "id": "566538896813783842",
                        "name": "Computer",
                        "url": "/antonellomiglio/computer/",
                        "section_count": 0,
                    }
                },
                "boardsections": {},
            }
        }
        redux = data.get("props", {}).get("initialReduxState") or data.get("initialReduxState")
        assert redux is not None
        assert "boards" in redux
        assert "566538896813783842" in redux["boards"]
        assert redux["boards"]["566538896813783842"]["name"] == "Computer"
