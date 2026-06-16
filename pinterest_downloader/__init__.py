"""Pinterest Downloader - Download images/videos from Pinterest boards, sections, and pins."""

__version__ = '2.0.0'


def run_main(path=None, **kwargs):
    """Run the Pinterest downloader programmatically."""
    from .orchestrator import run_library_main
    if path is None:
        path = input('Username/Boardname/Section or Link: ').strip()
    return run_library_main(
        arg_path=path, arg_dir=kwargs.get('dir', 'images'),
        arg_thread_max=kwargs.get('thread_max', 0), arg_cut=kwargs.get('cut', -1),
        arg_board_timestamp=kwargs.get('board_timestamp', False),
        arg_log_timestamp=kwargs.get('log_timestamp', False),
        arg_force=kwargs.get('force', False),
        arg_exclude_section=kwargs.get('exclude_section', False),
        arg_rescrape=kwargs.get('rescrape', False),
        arg_img_only=kwargs.get('img_only', False),
        arg_v_only=kwargs.get('v_only', False),
        arg_update_all=kwargs.get('update_all', False),
        arg_https_proxy=kwargs.get('https_proxy', None),
        arg_http_proxy=kwargs.get('http_proxy', None),
        arg_cookies=kwargs.get('cookies', None),
        arg_max_count=kwargs.get('max_count', 0),
        arg_quality=kwargs.get('quality', 'orig'),
        arg_dry_run=kwargs.get('dry_run', False),
        arg_delay=kwargs.get('delay', 0),
    )


def run_cli():
    """CLI entry point."""
    from .cli import main
    main()


if __name__ == '__main__':
    run_cli()
