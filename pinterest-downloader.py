#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pinterest Downloader - backward-compatible wrapper.

All logic has been moved to the pinterest_downloader/ package.
This file exists so that `python pinterest-downloader.py` still works.
"""
import sys
import os
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pinterest_downloader.ui import (
    IS_WIN, ANSI_CLEAR, HIGHER_RED, BOLD_ONLY, cprint,
    x_tag, done_tag, plus_tag, pinterest_logo,
)
from pinterest_downloader.orchestrator import run_library_main, update_all

try:
    print(pinterest_logo, end=ANSI_CLEAR, flush=True)
except Exception:
    cprint(''.join([HIGHER_RED, '%s' % ('Please run `export PYTHONIOENCODING=utf-8;` to support Unicode.')]),
           attrs=BOLD_ONLY, end='\n')
    sys.exit(1)

import argparse
import requests


def run_direct_main():
    arg_parser = argparse.ArgumentParser(
        description='Download ALL board/section from ' + pinterest_logo + 'interest by username, '
                    'username/boardname, username/boardname/section or link.')
    arg_parser.add_argument('path', nargs='?',
                           help='Pinterest username, or username/boardname, or username/boardname/section, or relevant link.')
    arg_parser.add_argument('-d', '--dir', dest='dir', type=str, default='images',
                           help='Specify folder path/name to store. Default is "images".')
    arg_parser.add_argument('-j', '--job', dest='thread_max', type=int, default=0,
                           help='Specify maximum threads when downloading images.')
    arg_parser.add_argument('-c', '--cut', type=int, default=-1,
                           help='Specify maximum length of "_TITLE_DESCRIPTION_DATE" in filename.')
    arg_parser.add_argument('-bt', '--board-timestamp', dest='board_timestamp', action='store_true',
                           help='Suffix board directory name with unique timestamp.')
    arg_parser.add_argument('-lt', '--log-timestamp', dest='log_timestamp', action='store_true',
                           help='Suffix log filename with unique timestamp.')
    arg_parser.add_argument('-co', '--cookies',
                           help='Set the cookies file to be used to login into Pinterest.')
    arg_parser.add_argument('-f', '--force', action='store_true',
                           help='Force re-download even if image already exist.')
    arg_parser.add_argument('-rs', '--re-scrape', dest='rescrape', action='store_true',
                           help='Re-scrape all images.')
    arg_parser.add_argument('-ua', '--update-all', dest='update_all', action='store_true',
                           help='Update all folders in current directory recursively.')
    arg_parser.add_argument('-es', '--exclude-section', dest='exclude_section', action='store_true',
                           help='Exclude sections if download from username or board.')
    arg_parser.add_argument('-io', '--image-only', dest='img_only', action='store_true',
                           help='Download image only.')
    arg_parser.add_argument('-vo', '--video-only', dest='v_only', action='store_true',
                           help='Download video only.')
    arg_parser.add_argument('-ps', '--https-proxy', help='Set proxy for https.')
    arg_parser.add_argument('-p', '--http-proxy', help='Set proxy for http.')
    arg_parser.add_argument('-n', '--max-count', dest='max_count', type=int, default=0,
                           help='Maximum number of pins to download per board/section.')
    arg_parser.add_argument('-q', '--quality', choices=['orig', '736x', '474x', '236x'], default='orig',
                           help='Image quality to download.')
    arg_parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                           help='Show what would be downloaded without downloading.')
    arg_parser.add_argument('--delay', type=float, default=0,
                           help='Delay in seconds between downloads.')

    try:
        args, remaining = arg_parser.parse_known_args()
    except SystemExit:
        return

    if remaining:
        return quit(['You type redundant options: ' + ' '.join(remaining),
                     'Please check your command or --help to see options manual.'])

    if not args.update_all and not args.path:
        args.path = input('Username/Boardname/Section or Link: ').strip()

    return run_library_main(args.path, args.dir, args.thread_max, args.cut,
                            args.board_timestamp, args.log_timestamp,
                            args.force, args.exclude_section, args.rescrape,
                            args.img_only, args.v_only, args.update_all,
                            args.https_proxy, args.http_proxy, args.cookies,
                            args.max_count, args.quality, args.dry_run, args.delay)


if __name__ == '__main__':
    try:
        run_direct_main()
    except requests.exceptions.ReadTimeout:
        cprint(''.join([HIGHER_RED, '{}'.format('\n[' + x_tag + '] Suddenly not able to connect. Please check your network.\n')]),
               attrs=BOLD_ONLY, end='')
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        cprint(''.join([HIGHER_RED, '{}'.format('\n[' + x_tag + '] Not able to connect. Please check your network.\n')]),
               attrs=BOLD_ONLY, end='')
        sys.exit(1)
    except Exception:
        cprint(''.join([HIGHER_RED, traceback.format_exc()]), attrs=BOLD_ONLY, end='\n')
        sys.exit(1)
