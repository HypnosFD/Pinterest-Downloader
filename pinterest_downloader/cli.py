"""Command-line interface for Pinterest Downloader."""

import argparse
import sys
import traceback

from .ui import IS_WIN, pinterest_logo, ANSI_CLEAR


def main():
    """CLI entry point with argument parsing."""
    try:
        print(pinterest_logo, end=ANSI_CLEAR, flush=True)
    except Exception:
        print('Please run with PYTHONIOENCODING=utf-8 to support Unicode.')
        sys.exit(1)

    from .orchestrator import run_library_main

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
                           help='Re-scrape all images instead of only fetching new ones.')
    arg_parser.add_argument('-ua', '--update-all', dest='update_all', action='store_true',
                           help='Update all folders in current directory recursively.')
    arg_parser.add_argument('-es', '--exclude-section', dest='exclude_section', action='store_true',
                           help='Exclude sections if download from username or board.')
    arg_parser.add_argument('-io', '--image-only', dest='img_only', action='store_true',
                           help='Download image only. Assumed -rs')
    arg_parser.add_argument('-vo', '--video-only', dest='v_only', action='store_true',
                           help='Download video only. Assumed -rs')
    arg_parser.add_argument('-ps', '--https-proxy', help='Set proxy for https.')
    arg_parser.add_argument('-p', '--http-proxy', help='Set proxy for http.')
    arg_parser.add_argument('-n', '--max-count', dest='max_count', type=int, default=0,
                           help='Maximum number of pins to download per board/section. 0 = unlimited.')
    arg_parser.add_argument('-q', '--quality', choices=['orig', '736x', '474x', '236x'], default='orig',
                           help='Image quality to download.')
    arg_parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                           help='Show what would be downloaded without actually downloading.')
    arg_parser.add_argument('--delay', type=float, default=0,
                           help='Delay in seconds between downloads (rate limiting).')

    try:
        args, remaining = arg_parser.parse_known_args()
    except SystemExit:
        return

    if remaining:
        print('You type redundant options: ' + ' '.join(remaining))
        print('Please check your command or --help to see options manual.')
        return

    if not args.update_all and not args.path:
        args.path = input('Username/Boardname/Section or Link: ').strip()

    try:
        run_library_main(
            arg_path=args.path, arg_dir=args.dir, arg_thread_max=args.thread_max,
            arg_cut=args.cut, arg_board_timestamp=args.board_timestamp,
            arg_log_timestamp=args.log_timestamp, arg_force=args.force,
            arg_exclude_section=args.exclude_section, arg_rescrape=args.rescrape,
            arg_img_only=args.img_only, arg_v_only=args.v_only,
            arg_update_all=args.update_all, arg_https_proxy=args.https_proxy,
            arg_http_proxy=args.http_proxy, arg_cookies=args.cookies,
            arg_max_count=args.max_count, arg_quality=args.quality,
            arg_dry_run=args.dry_run, arg_delay=args.delay,
        )
    except Exception:
        print(traceback.format_exc())


if __name__ == '__main__':
    main()
