"""Main orchestrator - dispatches to API, download, and filesystem modules."""

import os
import sys
import time
import traceback
from datetime import datetime, timedelta
from pathlib import PurePath
from urllib.parse import unquote

from .session import get_session, create_sessions, load_cookies
from .ui import (
    cprint, quit, IS_WIN, ANSI_CLEAR, ANSI_END_COLOR, ANSI_BLUE,
    HIGHER_RED, HIGHER_YELLOW, BOLD_ONLY, x_tag, done_tag, plus_tag,
    printProgressBar, pinterest_logo
)
from .paths import sanitize, get_max_path, get_output_file_path, create_dir
from .download import download_with_retry, download_img, isVideoExist, RETRY_TIMEOUTS
from .api import (
    get_pin_info, get_board_info, fetch_boards, fetch_imgs,
    write_log, get_latest_pin
)

WIN_MAX_PATH = 255
PAGE_SIZE = 25
MEDIA_EXTENSIONS = (
    '.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.mkv', '.webp',
    '.svg', '.m4a', '.mp3', '.flac', '.m3u8', '.wmv', '.webm', '.mov',
    '.flv', '.m4v', '.ogg', '.avi', '.wav', '.apng', '.avif',
)


def update_all(arg_thread_max, arg_cut, arg_rescrape, arg_img_only, arg_v_only,
               arg_https_proxy, arg_http_proxy, arg_cookies):
    bk_cwd = os.path.abspath(os.getcwd())
    cwd_component_total = len(PurePath(os.path.abspath(bk_cwd)).parts[:])
    imgs_f = []
    for root, dirs, files in os.walk(bk_cwd):
        imgs_f.extend([os.path.join(root, _) for _ in files if (_ == 'urls-pinterest-downloader.urls')])

    urls_map = {}
    cd_back_fixed_range = (1, 2, 3)
    for f in imgs_f:
        with open(f, "r", encoding="utf-8") as r:
            input_url = None
            folder_url = None
            for line in r:
                l_strip = line.strip()
                if l_strip.startswith('Input URL: '):
                    input_url = l_strip.split('Input URL: ')[1].strip()
                elif l_strip.startswith('Folder URL: '):
                    folder_url = l_strip.split('Folder URL: ')[1].strip()
                if input_url and folder_url:
                    cd_back_count = len(folder_url.split('/')[3:]) - 1
                    if cd_back_count not in cd_back_fixed_range:
                        os.chdir(bk_cwd)
                        return quit(['[E1][-ua] Input url: ' + input_url + '\nFolder url: ' + folder_url,
                                     'Something is not right.'])
                    dir_origin = os.path.abspath(os.path.join(f, '../' * (cd_back_count + 1)))
                    dir_split = PurePath(dir_origin).parts[:]
                    if len(dir_split) < cwd_component_total:
                        cprint(''.join([HIGHER_YELLOW, '%s' % ('\n' + 'Update from parent directory is forbidden. Skipped.\n')]))
                        break
                    if dir_origin in urls_map:
                        if cd_back_count in (2, 3):
                            urls_map[dir_origin]['info'].append({'url': folder_url, 'cd': cd_back_count})
                        elif cd_back_count == 1:
                            urls_map[dir_origin]['username'] = True
                    else:
                        urls_map[dir_origin] = {'info': [{'url': input_url, 'cd': cd_back_count}],
                                                'username': True if (cd_back_count == 1) else False}
                    break

    pre_calc_total = 0
    for i, (dir_origin, map_d) in enumerate(urls_map.items()):
        got_username = map_d['username']
        for info in map_d['info']:
            if got_username and info['cd'] == 2:
                continue
            pre_calc_total += 1
    real_run_index = 1
    for i, (dir_origin, map_d) in enumerate(urls_map.items()):
        os.chdir(dir_origin)
        got_username = map_d['username']
        for info in map_d['info']:
            if got_username and info['cd'] == 2:
                continue
            print('\n' + ANSI_BLUE + '[U] Updating [ ' + str(real_run_index) + ' / ' + str(pre_calc_total) + ' ] \n' + ANSI_END_COLOR + ANSI_BLUE + '[U] Changed to directory: ' + str(dir_origin).rstrip(os.sep) + os.sep + ANSI_END_COLOR)
            real_run_index += 1
            input_url = info['url']
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    run_library_main(input_url, '.', arg_thread_max, arg_cut, False, False, False, True,
                                     arg_rescrape, arg_img_only, arg_v_only, False, arg_https_proxy,
                                     arg_http_proxy, arg_cookies)
                    break
                except Exception:
                    if attempt < max_retries - 1:
                        cprint(''.join([HIGHER_RED, '{}'.format('\n[' + x_tag + '] [U] Connection error. Retrying ({}/{})...\n'.format(attempt + 1, max_retries))]),
                               attrs=BOLD_ONLY, end='')
                        time.sleep(5)
                    else:
                        cprint(''.join([HIGHER_RED, '{}'.format('\n[' + x_tag + '] [U] Failed after {} retries. Skipping.\n'.format(max_retries))]),
                               attrs=BOLD_ONLY, end='')
    os.chdir(bk_cwd)


def run_library_main(arg_path, arg_dir, arg_thread_max, arg_cut,
                     arg_board_timestamp, arg_log_timestamp,
                     arg_force, arg_exclude_section, arg_rescrape,
                     arg_img_only, arg_v_only, arg_update_all,
                     arg_https_proxy, arg_http_proxy, arg_cookies,
                     arg_max_count=0, arg_quality='orig', arg_dry_run=False,
                     arg_delay=0):

    if arg_img_only or arg_v_only:
        arg_rescrape = True

    if arg_update_all:
        return update_all(arg_thread_max, arg_cut, arg_rescrape, arg_img_only, arg_v_only,
                          arg_https_proxy, arg_http_proxy, arg_cookies)

    start_time = int(time.time())

    if not arg_path:
        return quit('Path cannot be empty. ')

    proxies = dict(http=arg_http_proxy, https=arg_https_proxy)
    cookies = str(arg_cookies)
    from .session import UA
    print('[i] User Agent: ' + UA)

    arg_path = arg_path.strip()
    if arg_path.startswith('https://pin.it/'):
        print('[i] Try to expand shorten url')
        from .session import get_session as _gs
        SHARE_SESSION = _gs(0, proxies, cookies)
        r = SHARE_SESSION.get(arg_path, timeout=(15, 15))
        if (r.status_code == 200) and '/sent' in r.url:
            arg_path = r.url.split('/sent')[0]
            print('[i] Pin url is: ' + arg_path + '/')

    url_path = arg_path.split('?')[0].split('#')[0]
    url_path = unquote(url_path).rstrip('/')
    if '://' in url_path:
        url_path = '/'.join(url_path.split('/')[3:])
        if not url_path:
            return quit('{} {} {}'.format('\n[' + x_tag + '] Neither username/boardname nor valid link: ', arg_path, '\n'))
    url_path = url_path.lstrip('/')
    slash_path = url_path.split('/')
    if '.' in slash_path[0]:
        slash_path = slash_path[1:]
    if len(slash_path) == 0:
        return quit('{} {} {}'.format('\n[' + x_tag + '] Neither username/boardname nor valid link: ', arg_path, '\n'))
    elif len(slash_path) > 3:
        return quit('[!] Something wrong with Pinterest URL.')

    cookie_file = cookies

    fs_f_max = None
    if IS_WIN:
        arg_el = True
        fs_f_max = WIN_MAX_PATH
    else:
        arg_el = False
        for fs_f_max_i in (255, 242, 143):
            try:
                with open('A' * fs_f_max_i, 'r') as f:
                    fs_f_max = fs_f_max_i
                    break
            except FileNotFoundError:
                fs_f_max = fs_f_max_i
                break
            except OSError:
                pass
        if fs_f_max is None:
            fs_f_max = os.statvfs('.').f_namemax

    if len(slash_path) == 2:
        if slash_path[-1].strip() in ('boards', '_saved', '_created', 'pins'):
            slash_path = slash_path[:-1]
        elif slash_path[-2].strip() == 'pin':
            print('[i] Job is download video/image of single pin page.')
            pin_id = slash_path[-1]
            slash_path = []
            sess = create_sessions(proxies, cookie_file)
            get_pin_info(pin_id.strip(), arg_log_timestamp, url_path, arg_force, arg_img_only,
                         arg_v_only, arg_dir, arg_cut, arg_el, fs_f_max, sess['image'], sess['video'],
                         sess['page'], proxies, cookie_file, False)

    if len(slash_path) == 3:
        sec_path = '/'.join(slash_path)
        board_path = '/'.join(slash_path[:-1])
        print('[i] Job is download single section by username/boardname/section: {}'.format(sec_path))
        if (slash_path[-3] in ('search', 'categories', 'topics')) or (slash_path[-1] in ['more_ideas']):
            return quit('{}'.format('\n[' + x_tag + '] Search, Categories, Topics, more_ideas are not supported.\n'))
        board = get_board_info(sec_path, False, slash_path[-1], board_path, proxies, cookie_file)
        try:
            sess = create_sessions(proxies, cookie_file)
            fetch_imgs(board, slash_path[-3], slash_path[-2], slash_path[-1], False,
                       arg_board_timestamp, arg_log_timestamp, url_path,
                       arg_force, arg_rescrape, arg_img_only, arg_v_only,
                       arg_dir, arg_thread_max,
                       sess['feed'], sess['image'], sess['video'], sess['page'], proxies,
                       cookie_file, arg_cut, arg_el, fs_f_max,
                       arg_max_count, arg_quality, arg_dry_run, arg_delay)
        except KeyError:
            return quit(traceback.format_exc())

    elif len(slash_path) == 2:
        board_path = '/'.join(slash_path)
        print('[i] Job is download single board by username/boardname: {}'.format(board_path))
        if slash_path[-2] in ('search', 'categories', 'topics'):
            return quit('{}'.format('\n[' + x_tag + '] Search, Categories and Topics not supported.\n'))
        board, sections = get_board_info(board_path, arg_exclude_section, None, None, proxies, cookie_file)
        try:
            sess = create_sessions(proxies, cookie_file)
            fetch_imgs(board, slash_path[-2], slash_path[-1], None, False,
                       arg_board_timestamp, arg_log_timestamp, url_path,
                       arg_force, arg_rescrape, arg_img_only, arg_v_only,
                       arg_dir, arg_thread_max,
                       sess['feed'], sess['image'], sess['video'], sess['page'], proxies,
                       cookie_file, arg_cut, arg_el, fs_f_max,
                       arg_max_count, arg_quality, arg_dry_run, arg_delay)
            if (not arg_exclude_section) and sections:
                sec_c = len(sections)
                print('[i] Trying to get ' + str(sec_c) + ' section{}'.format('s' if sec_c > 1 else ''))
                for sec in sections:
                    sec_path = board_path + '/' + sec['slug']
                    board = get_board_info(sec_path, False, sec['slug'], board_path, proxies, cookie_file)
                    fetch_imgs(board, slash_path[-2], slash_path[-1], sec['slug'], False,
                               arg_board_timestamp, arg_log_timestamp, url_path,
                               arg_force, arg_rescrape, arg_img_only, arg_v_only,
                               arg_dir, arg_thread_max,
                               sess['feed'], sess['image'], sess['video'], sess['page'], proxies,
                               cookie_file, arg_cut, arg_el, fs_f_max,
                               arg_max_count, arg_quality, arg_dry_run, arg_delay)
        except KeyError:
            return quit(traceback.format_exc())

    elif len(slash_path) == 1:
        print('[i] Job is download all boards by username: {}'.format(slash_path[-1]))
        if slash_path[-1] in ('search', 'categories', 'topics'):
            return quit('{}'.format('\n[' + x_tag + '] Search, Categories and Topics not supported.\n'))
        try:
            boards = fetch_boards(slash_path[-1], proxies, cookie_file)
            sess = create_sessions(proxies, cookie_file)
            for index, board in enumerate(boards):
                if 'name' not in board:
                    print('Skip no name')
                    continue
                board_path = board['url'].strip('/')
                if '/' in board_path:
                    board_slug = board_path.split('/')[1]
                    is_main_board = False
                else:
                    board_slug = board_path
                    is_main_board = True
                board['owner']['id'] = board['id']

                fetch_imgs(board, slash_path[-1], board_slug, None, is_main_board,
                           arg_board_timestamp, arg_log_timestamp, url_path,
                           arg_force, arg_rescrape, arg_img_only, arg_v_only,
                           arg_dir, arg_thread_max,
                           sess['feed'], sess['image'], sess['video'], sess['page'], proxies,
                           cookie_file, arg_cut, arg_el, fs_f_max,
                           arg_max_count, arg_quality, arg_dry_run, arg_delay)
                if (not arg_exclude_section) and (board['section_count'] > 0):
                    sec_c = board['section_count']
                    print('[i] Trying to get ' + str(sec_c) + ' section{}'.format('s' if sec_c > 1 else ''))
                    board, sections = get_board_info(board_path, False, None, None, proxies, cookie_file)
                    for sec in sections:
                        sec_path = board_path + '/' + sec['slug']
                        board = get_board_info(sec_path, False, sec['slug'], board_path, proxies, cookie_file)
                        sec_uname, sec_bname = board_path.split('/')
                        fetch_imgs(board, sec_uname, sec_bname, sec['slug'], False,
                                   arg_board_timestamp, arg_log_timestamp, url_path,
                                   arg_force, arg_rescrape, arg_img_only, arg_v_only,
                                   arg_dir, arg_thread_max,
                                   sess['feed'], sess['image'], sess['video'], sess['page'], proxies,
                                   cookie_file, arg_cut, arg_el, fs_f_max,
                                   arg_max_count, arg_quality, arg_dry_run, arg_delay)
        except KeyError:
            return quit(traceback.format_exc())

    end_time = int(time.time())
    try:
        print('[i] Time Spent: ' + str(timedelta(seconds=end_time - start_time)))
    except OverflowError:
        print('Can you revive me please? Thanks.')
