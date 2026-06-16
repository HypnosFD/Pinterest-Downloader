<h align="center">

  pinterest-downloader

  <br>

  Download all images & videos from Pinterest boards, sections, and pins.

  [![CI](https://github.com/HypnosFD/pinterest-downloader/actions/workflows/ci.yml/badge.svg)](https://github.com/HypnosFD/pinterest-downloader/actions/workflows/ci.yml)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
  [![Tests](https://img.shields.io/badge/tests-44%20passed-brightgreen)](tests/)

</h>

<br>

## Overview

A fast, reliable CLI tool to batch-download images and videos from Pinterest. Supports downloading by **username**, **board**, **section**, or **single pin** — with incremental updates, multi-threading, and proxy support.

> **Forked from** [limkokhole/pinterest-downloader](https://github.com/limkokhole/pinterest-downloader)

---

## Features

<table>
<tr><td>

**Download Modes**
- By **username** — all boards
- By **username/boardname** — all pins
- By **username/boardname/section** — specific section
- **Single pin** by URL or ID
- Expand shortened `pin.it` links

</td><td>

**Quality & Performance**
- Original resolution (or 736x, 474x, 236x)
- Both images and videos
- Multi-threaded downloads
- Rate limiting with `--delay`
- Retry with exponential backoff

</td></tr>
<tr><td>

**Smart Features**
- Incremental updates (new pins only)
- Max count limit (`-n`)
- Dry run mode (`--dry-run`)
- LD+JSON fallback parsing

</td><td>

**File Management**
- Meaningful filenames with metadata
- Auto-truncation for filesystem limits
- Windows extended-length paths
- Timestamp suffixes for boards/logs
- Detailed log files

</td></tr>
<tr><td>

**Network & Auth**
- Cookie/token support for private boards
- HTTP and SOCKS proxy support
- Automatic CSRF token handling

</td><td>

**Bulk Operations**
- Update all folders (`-ua`)
- Exclude sections (`-es`)
- Image-only (`-io`) or video-only (`-vo`)

</td></tr>
</table>

---

## Quick Start

### From Source

```bash
git clone https://github.com/HypnosFD/pinterest-downloader.git
cd pinterest-downloader
pip install -r requirements.txt
```

### Via pip (Development)

```bash
pip install -e .
```

---

## Usage

```bash
# Interactive mode
python pinterest-downloader.py

# Download all boards from a user
python pinterest-downloader.py antonellomiglio

# Download a specific board
python pinterest-downloader.py antonellomiglio/computer

# Download a section
python pinterest-downloader.py antonellomiglio/computer/condiments

# Download a single pin
python pinterest-downloader.py https://www.pinterest.com/pin/566538828106779478/

# Download with options
python pinterest-downloader.py antonellomiglio/computer -d my_images -n 10 -q 736x

# Preview without downloading
python pinterest-downloader.py antonellomiglio/computer --dry-run

# Update all previously downloaded folders
python pinterest-downloader.py -ua

# Use cookies for private boards
python pinterest-downloader.py antonellomiglio/secret-board -co cookies.txt
```

### Via Module

```bash
python -m pinterest_downloader antonellomiglio/computer
```

### Programmatic Usage

```python
from pinterest_downloader import run_main

run_main(
    path='antonellomiglio/computer',
    dir='my_images',
    quality='736x',
    max_count=10,
)
```

---

## Options

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

---

## Cookie Setup for Private Boards

1. Log into Pinterest in your browser
2. Export cookies using a browser extension (e.g., [Get Token Cookie](https://chrome.google.com/webstore/detail/get-token-cookie/naciaagbkifhpnoodlkhbejjldaiffcm))
3. Save cookies to `cookies.txt` in the project directory
4. Run with `-co cookies.txt`

---

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
tests/                           # Unit tests
.github/workflows/ci.yml        # GitHub Actions CI
pyproject.toml                   # Package configuration
requirements.txt                 # Dependencies
```

---

## Requirements

- Python 3.8+
- See `requirements.txt` for full dependency list

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Credits

- **Original author:** [limkokhole](https://github.com/limkokhole)
- **Fork maintainer:** [HypnosFD](https://github.com/HypnosFD)
