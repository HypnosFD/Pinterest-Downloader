"""Tests for download utilities."""

import os
import pytest
import sys
import requests
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from pinterest_downloader.download import isVideoExist, download_with_retry, RETRY_TIMEOUTS
import pinterest_downloader.download as dl_mod


class TestIsVideoExist:
    def test_no_video(self):
        image = {"id": "123", "images": {"orig": {"url": "test.jpg"}}}
        assert isVideoExist(image) == 0

    def test_video_type_1(self):
        image = {
            "id": "123",
            "videos": {"video_list": {"V_720P": {"url": "test.mp4"}}},
        }
        assert isVideoExist(image) == 1

    def test_video_type_2(self):
        image = {
            "id": "123",
            "story_pin_data": {
                "pages": [{"blocks": [{"video": {"video_list": {"V_EXP7": {"url": "test.mp4"}}}}]}]
            },
        }
        assert isVideoExist(image) == 2

    def test_empty_videos(self):
        image = {"id": "123", "videos": None}
        assert isVideoExist(image) == 0

    def test_empty_story_pin_data(self):
        image = {"id": "123", "story_pin_data": None}
        assert isVideoExist(image) == 0


class TestRetryTimeouts:
    def test_values(self):
        assert RETRY_TIMEOUTS == (15, 30, 40, 50, 60)
        assert len(RETRY_TIMEOUTS) == 5


class TestDownloadWithRetry:
    def test_successful_download(self, tmp_path):
        mock_session = MagicMock()
        mock_response = MagicMock()
        mock_response.ok = True
        mock_response.__iter__ = lambda self: iter([b"test data"])
        mock_session.get.return_value = mock_response

        file_path = str(tmp_path / "test.jpg")
        success, session = download_with_retry(
            mock_session, "http://example.com/test.jpg", file_path, {}, None
        )
        assert success is True
        assert os.path.exists(file_path)

    def test_failed_download(self, tmp_path):
        mock_session = MagicMock()
        mock_session.get.side_effect = requests.exceptions.ConnectionError("Connection failed")

        file_path = str(tmp_path / "test.jpg")
        with patch.object(dl_mod, 'get_session', return_value=mock_session):
            with patch('time.sleep'):
                success, session = download_with_retry(
                    mock_session, "http://example.com/test.jpg", file_path, {}, None
                )
        assert success is False
