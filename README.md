# pinterest-downloader

Download all images/videos from Pinterest user/board/section.

[![CI](https://github.com/HypnosFD/pinterest-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/HypnosFD/pinterest-downloader/actions/workflows/ci.yml)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

### Download Modes
- [x] Download by **username** — all boards from a user
- [x] Download by **username/boardname** — all pins from a board
- [x] Download by **username/boardname/section** — pins from a specific section
- [x] Download **single pin** by URL or Pin ID
- [x] Accept full URL or shorthand format (`username/boardname`)
- [x] Expand shortened `pin.it` share links

### Quality & Format
- [x] Download images at **original resolution** (or choose 736x, 474x, 236x)
- [x] Download **both images and videos** with automatic quality selection
- [x] Fallback to second-best resolution on download error
- [x] LD+JSON fallback for pin page parsing

### Smart Features
- [x] **Incremental updates** — only download new pins since last run
- [x] **Max count limit** (`-n`) — download only N pins per board
- [x] **Dry run mode** (`--dry-run`) — preview what would be downloaded
- [x] **Rate limiting** (`--delay`) — add delay between downloads
- [x] **Multi-threaded** downloads for speed

### File Management
- [x] Meaningful filenames: `PinID_Title_Description_Date.ext`
- [x] Automatic filename truncation to fit filesystem limits
- [x] Windows extended-length path support (`\\?\`)
- [x] Timestamp suffixes for boards and logs
- [x] Detailed log file with pin metadata

### Network & Auth
- [x] **Cookie/token support** for private/secret boards
- [x] **Proxy support** (HTTP and HTTPS/SOCKS)
- [x] Automatic CSRF token handling
- [x] Retry with exponential backoff on failures

### Bulk Operations
- [x] **Update all** (`-ua`) — recursively update all downloaded folders
- [x] **Exclude sections** (`-es`) from board downloads
- [x] **Image-only** (`-io`) or **video-only** (`-vo`) modes

## Installation

### From source (recommended)

```bash
git clone https://github.com/HypnosFD/pinterest-downloader.git
cd pinterest-downloader
pip install -r requirements.txt
```

### Via pip (development)

```bash
pip install -e .
```

## Usage

### Command Line

```bash
# Interactive mode — prompts for path
python pinterest-downloader.py

# Download all boards from a user
python pinterest-downloader.py antonellomiglio

# Download a specific board
python pinterest-downloader.py antonellomiglio/computer

# Download a section
python pinterest-downloader.py antonellomiglio/computer/condiments

# Download a single pin
python pinterest-downloader.py https://www.pinterest.com/pin/566538828106779478/

# Download with custom output directory
python pinterest-downloader.py antonellomiglio/computer -d my_images

# Download only 10 pins (max count)
python pinterest-downloader.py antonellomiglio/computer -n 10

# Download at 736x quality (faster, smaller files)
python pinterest-downloader.py antonellomiglio/computer -q 736x

# Preview what would be downloaded (dry run)
python pinterest-downloader.py antonellomiglio/computer --dry-run

# Rate limit: 1 second delay between downloads
python pinterest-downloader.py antonellomiglio/computer --delay 1

# Force re-download all files
python pinterest-downloader.py antonellomiglio/computer -f -rs

# Download only images (skip videos)
python pinterest-downloader.py antonellomiglio/computer -io

# Download with proxy
python pinterest-downloader.py antonellomiglio/computer -ps "socks5://proxy:1080"

# Use cookies for private boards
python pinterest-downloader.py antonellomiglio/secret-board -co cookies.txt

# Update all previously downloaded folders
python pinterest-downloader.py -ua
```

### Via pip entry point

```bash
pip install -e .
pinterest-downloader antonellomiglio/computer
```

### As a Python module

```bash
python -m pinterest_downloader antonellomiglio/computer
```

### Programmatic usage

```python
from pinterest_downloader import run_main

# Download a board
run_main(
    path='antonellomiglio/computer',
    dir='my_images',
    quality='736x',
    max_count=10,
)

# Or use the orchestrator directly
from pinterest_downloader.orchestrator import run_library_main

run_library_main(
    arg_path='antonellomiglio/computer',
    arg_dir='my_images',
    arg_thread_max=0,
    arg_cut=-1,
    arg_board_timestamp=False,
    arg_log_timestamp=False,
    arg_force=False,
    arg_exclude_section=False,
    arg_rescrape=False,
    arg_img_only=False,
    arg_v_only=False,
    arg_update_all=False,
    arg_https_proxy=None,
    arg_http_proxy=None,
    arg_cookies=None,
    arg_max_count=10,
    arg_quality='736x',
    arg_dry_run=False,
    arg_delay=0,
)
```

## All Options

| Short | Long | Description |
|-------|------|-------------|
| `-d` | `--dir DIR` | Output directory (default: `images`) |
| `-j` | `--job N` | Max download threads |
| `-c` | `--cut N` | Max filename title length |
| `-n` | `--max-count N` | Max pins to download per board |
| `-q` | `--quality` | Image quality: `orig`, `736x`, `474x`, `236x` |
| `-f` | `--force` | Force re-download existing files |
| `-rs` | `--re-scrape` | Re-scrape all pins (ignore incremental) |
| `-bt` | `--board-timestamp` | Add timestamp to board directory names |
| `-lt` | `--log-timestamp` | Add timestamp to log filenames |
| `-es` | `--exclude-section` | Skip board sections |
| `-io` | `--image-only` | Download images only |
| `-vo` | `--video-only` | Download videos only |
| `-ua` | `--update-all` | Update all downloaded folders |
| `-ps` | `--https-proxy` | HTTPS proxy URL |
| `-p` | `--http-proxy` | HTTP proxy URL |
| `-co` | `--cookies FILE` | Cookie file for private boards |
| | `--dry-run` | Preview without downloading |
| | `--delay SECS` | Delay between downloads (rate limit) |

## Project Structure

```
pinterest-downloader.py          # Backward-compatible entry point
pinterest_downloader/            # Main package
    __init__.py                  # Package API (run_main)
    __main__.py                  # python -m entry point
    config.py                    # Shared constants
    ui.py                        # Terminal output & colors
    session.py                   # HTTP sessions & cookies
    paths.py                     # File path handling
    download.py                  # Download logic & retry
    api.py                       # Pinterest API interaction
    orchestrator.py              # Main workflow dispatcher
    cli.py                       # CLI argument parsing
tests/                           # Unit tests (44 tests)
.github/workflows/ci.yml        # GitHub Actions CI
pyproject.toml                   # Package configuration
requirements.txt                 # Dependencies
```

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## Cookie Setup for Private Boards

1. Log into Pinterest in your browser
2. Use a cookie export extension (e.g., [Get Token Cookie](https://chrome.google.com/webstore/detail/get-token-cookie/naciaagbkifhpnoodlkhbejjldaiffcm))
3. Save cookies to `cookies.txt` in the project directory
4. Run with `-co cookies.txt`

## License

MIT License - see [LICENSE](LICENSE) for details.
