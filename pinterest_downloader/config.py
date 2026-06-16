"""Configuration constants for Pinterest Downloader."""

import platform

# Platform detection
IS_WIN = ('window' in platform.system().lower()) or platform.system().lower().startswith('win')

# ANSI color codes
if IS_WIN:
    ANSI_CLEAR = '\r'
    ANSI_END_COLOR = ''
    ANSI_BLUE = ''
else:
    ANSI_CLEAR = '\r\x1b[0m\x1b[K'
    ANSI_END_COLOR = '\x1b[0m\x1b[K'
    ANSI_BLUE = '\x1b[1;44m'

# Filesystem
WIN_MAX_PATH = 255

# Retry configuration
RETRY_TIMEOUTS = (15, 30, 40, 50, 60)
RETRY_SLEEP_SECONDS = 5

# Pinterest API
PAGE_SIZE = 25
PINTEREST_BASE_URL = 'https://www.pinterest.com'
VER = (None, '977943c', '4c8c36f')

# Media file extensions
MEDIA_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.mkv', '.webp',
    '.svg', '.m4a', '.mp3', '.flac', '.m3u8', '.wmv', '.webm', '.mov',
    '.flv', '.m4v', '.ogg', '.avi', '.wav', '.apng', '.avif',
)

# UI symbols
X_TAG = '✖'
DONE_TAG = '✔'
PLUS_TAG = '➕'
PINTEREST_LOGO = '🅿️'
