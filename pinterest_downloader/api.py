import json
import time
import os
import urllib
from urllib.parse import unquote
import lxml.html as html
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import sys
import traceback

from .session import get_session, load_cookies, UA
from .ui import (cprint, quit, HIGHER_RED, HIGHER_YELLOW, BOLD_ONLY,
                 x_tag, done_tag, plus_tag, printProgressBar, ANSI_BLUE, ANSI_END_COLOR)
from .download import (download_with_retry, isVideoExist, download_img, RETRY_TIMEOUTS)
from .paths import (get_output_file_path, create_dir, sanitize, get_max_path)

PAGE_SIZE = 25
MEDIA_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.mp4', '.mkv', '.webp', '.svg', '.m4a', '.mp3', '.flac', '.m3u8', '.wmv', '.webm', '.mov', '.flv', '.m4v', '.ogg', '.avi', '.wav', '.apng', '.avif')
IS_WIN = sys.platform == 'win32'


def write_log(arg_timestamp_log, url_path, shortform
    , arg_img_only, arg_v_only
    , save_dir, images, pin, arg_cut, break_from_latest_pin):

    got_img = False
    
    if arg_timestamp_log:
        if pin:
            log_timestamp = 'log-pinterest-downloader_' + str(pin) + '_' + datetime.now().strftime('%Y-%m-%d %H.%M.%S')
        else:
            log_timestamp = 'log-pinterest-downloader_' + datetime.now().strftime('%Y-%m-%d %H.%M.%S')
    else:
        if pin:
            log_timestamp = 'log-pinterest-downloader_' + str(pin)
        else:
            log_timestamp = 'log-pinterest-downloader'
    log_path = os.path.join(save_dir, '{}'.format( sanitize(log_timestamp) + '.log' ))

    if not pin:
        log_url_path = os.path.join(save_dir, 'urls-pinterest-downloader.urls')

        with open(log_url_path, 'w', encoding="utf-8") as f:
            f.write('Pinterest Downloader\n\n')
            f.write('Input URL: https://www.pinterest.com/' + url_path.rstrip('/')  + '/\n')
            if shortform:
                f.write('Folder URL: https://www.pinterest.com/' + shortform.rstrip('/') + '/\n\n')

    if images:
        index_last = 0
        existing_indexes = []

        if break_from_latest_pin and not arg_timestamp_log:
            try:
                with open(log_path, encoding="utf-8") as f:
                    index_line = [l for l in f.readlines() if l.startswith('[ ')]
                    index_last_tmp = index_line[-1].split('[ ')[1].split(' ]')[0]
                    if index_last_tmp.isdigit():
                        index_last = int(index_last_tmp)
                    for l in index_line:
                        existing_indexes.append(l.split('[ ')[1].split(' ] Pin Id: ')[1].strip())
            except (FileNotFoundError, OSError, KeyError, TypeError):
                cprint(''.join([ HIGHER_YELLOW, '%s' % ('\nWrite log increment from last log stored index failed. Fallback to -lt\n\n') ]), attrs=BOLD_ONLY, end='' )  
                log_timestamp = 'log-pinterest-downloader_' + datetime.now().strftime('%Y-%m-%d %H.%M.%S')
                log_path = os.path.join(save_dir, '{}'.format( sanitize(log_timestamp) + '.log' ))
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write('Pinterest Downloader\n\n')
        else:
            if pin:
                img_total = 1
            elif break_from_latest_pin:
                img_total = len(images)
            else:
                img_total = len(images) - 1
                if img_total == 0:
                    if ( (not arg_img_only and isVideoExist(images[0])) \
                        or (not arg_v_only and ('images' in images[0])) ):
                        img_total = 1
            if img_total == 0:
                return False
            else:
                with open(log_path, 'w', encoding='utf-8') as f:
                    f.write('Pinterest Downloader\n\n')
                    f.write('Input URL: https://www.pinterest.com/' + url_path.rstrip('/')  + '/\n')
                    if shortform:
                        f.write('Folder URL: https://www.pinterest.com/' + shortform.rstrip('/') + '/\n\n')
                    else:
                        f.write('\n')
        skipped_total = 0
        for log_i, image in enumerate(images):
            if 'id' not in image:
                skipped_total+=1
                continue
            got_img = True
            image_id = image['id']
            if image_id in existing_indexes: 
                print('dup image_id ' + str(image_id))
                continue
            if not ( (not arg_img_only and isVideoExist(image)) \
                    or (not arg_v_only and ('images' in image)) ):
                skipped_total+=1
                continue

            story = ''
            if ('grid_title' in image) and image['grid_title']:
                story = '\nTitle: ' + image['grid_title'].replace('\n', ' ').strip()
            if ('closeup_unified_description' in image) and image['closeup_unified_description'] and image['closeup_unified_description'].strip():
                story += '\nDescription: ' + image['closeup_unified_description'].replace('\n', ' ').strip()
            elif ('description' in image) and image['description'] and image['description'].strip():
                story += '\nDescription: ' + image['description'].replace('\n', ' ').strip()
            if ('created_at' in image) and image['created_at']:
                story += '\nCreated at: ' + image['created_at'].replace('\n', ' ').strip()
            if ('link' in image) and image['link']:
                story += '\nLink: ' + image['link'].replace('\n', ' ').strip()
            if ('rich_metadata' in image) and image['rich_metadata']:
                story += '\n\nMetadata: ' + repr(image['rich_metadata']).replace('\n', ' ').strip()
            if story:
                try:
                    with open(log_path, 'a', encoding='utf-8') as f:
                        f.write('[ ' + str(index_last + log_i + 1 - skipped_total) + ' ] Pin Id: ' + str(image_id) + '\n')
                        f.write(story + '\n\n')
                except OSError:
                    cprint(''.join([ HIGHER_RED, '%s' % ('\nYou may want to use -c <Maximum length of filename>\n\n') ]), attrs=BOLD_ONLY, end='' )  
                    return quit(traceback.format_exc())
            else:
                skipped_total+=1
                continue

    return got_img


def sort_func(x):
    prefix = x.split('.')[0].split('_')[0]
    if prefix.isdigit():
       return int(prefix)
    return 0


def get_latest_pin(save_dir):
    latest_pin = '0'
    depth = 1
    walk_dir = os.path.abspath(save_dir)
    for root, dirs, files in os.walk(walk_dir):
        if root[len(walk_dir):].count(os.sep) < depth:
            imgs_f = [_ for _ in files if _.lower().endswith(MEDIA_EXTENSIONS) ]
            imgs_f_sorted = sorted(imgs_f, key=sort_func)
            if not imgs_f_sorted:
                break
            latest_pin = imgs_f_sorted[-1].split('.')[0].split('_')[0]

    return latest_pin


def get_pin_info(pin_id, arg_timestamp_log, url_path
    , arg_force_update, arg_img_only, arg_v_only
    , arg_dir, arg_cut, arg_el, fs_f_max
    , IMG_SESSION, V_SESSION, PIN_SESSION, proxies
    , cookie_file, get_data_only):

    scripts = []
    is_success = False
    image = None
    r = None
    for t in RETRY_TIMEOUTS:
        cookies = load_cookies(cookie_file)
        
        try:
            r = PIN_SESSION.get('https://www.pinterest.com/pin/{}/'.format(pin_id), timeout=(t, t), cookies=cookies)
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            time.sleep(5)
            PIN_SESSION = get_session(0, proxies, cookie_file)
            continue

        root = html.fromstring(r.content)
        try:
            scripts = root.xpath('//script/text()')
        except IndexError:
            time.sleep(5)
            PIN_SESSION = get_session(0, proxies, cookie_file)
            continue

        indexErr = False
        for script in scripts:
            if not script.strip():
                continue
            try:
                data = json.loads(script)
                if not isinstance(data, dict):
                    continue
                redux = data.get('props', {}).get('initialReduxState') or data.get('initialReduxState')
                if redux and 'pins' in redux:
                    pins = redux['pins']
                    try:
                        image = pins[list(pins.keys())[0]]
                        is_success = True
                        break
                    except IndexError:
                        indexErr = True
            except json.decoder.JSONDecodeError:
                pass

        if not is_success:
            if indexErr:
                print('\n[Retry] Getting error pin id: ' + repr(pin_id) + '...\n\n')
            continue

    if not is_success:
        ld_scripts = root.xpath('//script[@type="application/ld+json"]/text()')
        for ld_text in ld_scripts:
            try:
                ld_data = json.loads(ld_text)
                if ld_data.get('@type') == 'SocialMediaPosting' and ld_data.get('image'):
                    image_url = ld_data['image']
                    if isinstance(image_url, dict):
                        image_url = image_url.get('url', '')
                    if image_url:
                        image = {
                            'id': pin_id,
                            'images': {
                                'orig': {'url': image_url}
                            },
                            'description': ld_data.get('articleBody', ''),
                        }
                        is_success = True
                        break
            except (json.decoder.JSONDecodeError, ValueError):
                pass

    if not is_success:
        if not get_data_only:
            print('### HTML START ###')
            if r is not None:
                print(r.content)
            print('### HTML END ###\n\nPlease report this issue at https://github.com/HypnosFD/pinterest-downloader/issues , thanks.\n\n')
            cprint(''.join([ HIGHER_RED, '%s %s%s' % ('\n[' + x_tag 
                + '] Get this pin id failed :', pin_id, '\n') ]), attrs=BOLD_ONLY, end='' )
        return

    if get_data_only:
        return image
    try:
        create_dir(arg_dir)
        write_log( arg_timestamp_log, url_path, None, arg_img_only, arg_v_only, arg_dir, [image], image['id'], arg_cut, False )
        print('[i] Download Pin id: ' + str(image['id']) + ' into directory: ' + arg_dir.rstrip(os.sep) + os.sep)
        printProgressBar(0, 1, prefix='[...] Downloading:', suffix='Complete', length=50)
        download_img(image, arg_dir, arg_force_update, arg_img_only, arg_v_only, IMG_SESSION, V_SESSION, PIN_SESSION, proxies, cookie_file, arg_cut, arg_el, fs_f_max)
        printProgressBar(1, 1, prefix='[' + done_tag + '] Downloaded:', suffix='Complete   ', length=50)
    except KeyError:
        return quit(traceback.format_exc())
    print()


def get_board_info(board_or_sec_path, exclude_section, section, board_path, proxies, cookie_file, retry=False):
    cookies = load_cookies(cookie_file)
        
    s = get_session(0, proxies, cookie_file)

    boards = {}
    sections = []

    is_success = False
    for t in RETRY_TIMEOUTS:
        cookies = load_cookies(cookie_file)
        try:
            r = s.get('https://www.pinterest.com/{}/'.format(board_or_sec_path), timeout=(t, t), cookies=cookies)
            is_success = True
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            time.sleep(5)
            s = get_session(0, proxies, cookie_file)

    if is_success:
        root = html.fromstring(r.content)
        scripts = root.xpath('//script/text()')
        board_d = {}
        board_sec_d = {}
        for script in scripts:
            if not script.strip():
                continue
            try:
                data = json.loads(script)
                if not isinstance(data, dict):
                    continue
                redux = data.get('props', {}).get('initialReduxState') or data.get('initialReduxState')
                if redux and 'boards' in redux:
                    board_d = redux['boards']
                    board_sec_d = redux.get('boardsections', {})
                    is_success = True
                    break
            except json.decoder.JSONDecodeError:
                is_success = False
            
    if not is_success:
        cprint(''.join([ HIGHER_RED, '%s %s%s' % ('\n[' + x_tag 
            + '] Get this board/section failed :', board_or_sec_path, '\n') ]), attrs=BOLD_ONLY, end='' )
        if section:
            return boards
        else:
            return boards, sections

    board_dk = list(board_d.keys())
    if section:
        path_to_compare = board_path
    else:
        path_to_compare = board_or_sec_path
    for k in board_dk:
        if unquote(board_d[k].get('url', '').strip('/')) == unquote(path_to_compare):
            b_dk = board_d[k]
            board_d_map = {}
            board_d_map['url'] = b_dk.get('url', '')
            board_d_map['id'] = b_dk.get('id', '')
            board_d_map['name'] = b_dk.get('name', '')
            board_d_map['section_count'] = b_dk.get('section_count', '')
            boards['board'] = board_d_map;
            break
        
    if not exclude_section:
        board_sec_dk = list(board_sec_d.keys())
        for k in board_sec_dk:
            b_dk = board_sec_d[k]
            sec_d_map = {}
            sec_slug = unquote(b_dk.get('slug', ''))
            if section and (sec_slug != section):
                continue

            sec_d_map['slug'] = sec_slug
            sec_d_map['id'] = b_dk.get('id', '')
            sec_d_map['title'] = b_dk.get('title', '')

            if section:
                boards['section'] = sec_d_map
            else:
                sections.append(sec_d_map)

    if section:
        return boards
    else:
        return boards, sections


def fetch_boards(uname, proxies, cookie_file):

    cookies = load_cookies(cookie_file)
        
    s = get_session(1, proxies, cookie_file)

    bookmark = None
    boards = []

    while bookmark != '-end-':

        options = {
        'isPrefetch': 'false',
        'privacy_filter': 'all',
        'sort': 'alphabetical', 
        'field_set_key': 'profile_grid_item',
        'username': uname,
        'page_size': PAGE_SIZE,
        'group_by': 'visibility',
        'include_archived': 'true',
        'redux_normalize_feed': 'true',
        }

        if bookmark:
            options.update({
                'bookmarks': [bookmark],
            })

        b_len = len(boards) - 1
        if b_len < 0:
            b_len = 0
        print('\r[...] Getting all boards [ ' + str(b_len) + ' / ? ]' , end='')
        sys.stdout.flush()

        post_d = urllib.parse.urlencode({
            'source_url': uname,
            'data': {
                'options': options,
                'context': {}
            },
            '_': int(time.time()*1000)
        }).replace('+', '').replace('%27', '%22') \
        .replace('%3A%22true%22', '%3Atrue').replace('%3A%22false%22', '%3Afalse')

        is_success = False
        for t in RETRY_TIMEOUTS:
            cookies = load_cookies(cookie_file)
            try:  
                r = s.get('https://www.pinterest.com/resource/BoardsResource/get/', params=post_d, timeout=(t, t), cookies=cookies)
                is_success = True
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                time.sleep(5)
                s = get_session(1, proxies, cookie_file)
        if not is_success:
            cprint(''.join([ HIGHER_RED, '%s %s%s' % ('\n[' + x_tag 
                + '] Get this username failed :', uname, '\n') ]), attrs=BOLD_ONLY, end='' )
            break
        data = r.json()
        try:
            boards.extend(data['resource_response']['data'])
            bookmark = data['resource']['options']['bookmarks'][0]
        except TypeError:
            cprint(''.join([ HIGHER_RED, '%s' % ('\n[' + x_tag + '] Possible invalid username.\n\n') ]), attrs=BOLD_ONLY, end='' ) 
            break

    b_len = len(boards)
    print('[' + plus_tag + '] Found {} Board{}.'.format(b_len, 's' if b_len > 1 else ''))

    return boards


def fetch_imgs(board, uname, board_slug, section_slug, is_main_board
    , arg_timestamp, arg_timestamp_log, url_path
    , arg_force_update, arg_rescrape, arg_img_only, arg_v_only
    , arg_dir, arg_thread_max
    , IMGS_SESSION, IMG_SESSION, V_SESSION, PIN_SESSION, proxies
    , cookie_file, arg_cut, arg_el, fs_f_max
    , arg_max_count=0, arg_quality='orig', arg_dry_run=False, arg_delay=0):
    
    bookmark = None
    images = []

    if is_main_board:
        shortform = uname
    else:
        if section_slug:
            shortform = '/'.join((uname, board_slug, section_slug))
        else:
            shortform = '/'.join((uname, board_slug))
    
    if arg_timestamp:
        timestamp_d = '_' + datetime.now().strftime('%Y-%m-%d %H.%M.%S') + '.d'
    else:
        timestamp_d = ''
    try:
        if 'owner' in board:
            bid = board['id']
            board_name_folder = board['name']
        elif 'board' in board:
            bid = board['board']['id']
            board_name_folder = board['board']['name']
            if section_slug:
                try:
                    section_id = board['section']['id']
                except (KeyError, TypeError):
                    return quit('{}'.format('\n[' + x_tag + '] Section may not exist.\n') )
                section_folder = board['section']['title']
        else:
            return quit('{}'.format('\n[' + x_tag + '] No item found.\n\
Please ensure your username/boardname/[section] or link has media item.\n') )
    except (KeyError, TypeError):
        cprint(''.join([ HIGHER_RED, '%s %s %s' % ('\n[' + x_tag + '] Failed. Path:', shortform, '\n\n') ]), attrs=BOLD_ONLY, end='' )
        return quit(traceback.format_exc() + '\n[!] Something wrong with Pinterest URL. Please report this issue at https://github.com/HypnosFD/pinterest-downloader/issues , thanks.') 

    fs_d_max = fs_f_max

    if section_slug:
        save_dir = os.path.join( arg_dir,  get_max_path(-1, fs_d_max, sanitize(uname), None)
            , get_max_path(-1, fs_d_max, sanitize(board_name_folder + timestamp_d), None)
            , get_max_path(-1, fs_d_max, sanitize(section_folder), None) )
        url = '/' + '/'.join((uname, board_slug, section_slug)) + '/'
    else:
        save_dir = os.path.join( arg_dir,  get_max_path(-1, fs_d_max, sanitize(uname), None)
            , get_max_path(-1, fs_d_max, sanitize(board_name_folder + timestamp_d), None))
        if is_main_board:
            url = uname
        else:
            url = '/'.join((uname, board_slug))

    if not arg_rescrape:
        latest_pin = get_latest_pin(save_dir)

    break_from_latest_pin = False
    sorted_api = True
    while bookmark != '-end-':

        if section_slug:

            options = {
            'isPrefetch': 'false',
            'field_set_key': 'react_grid_pin',
            'is_own_profile_pins': 'false',
            'page_size': PAGE_SIZE,
            'redux_normalize_feed': 'true',
            'section_id': section_id,
            }

        else:
            options = {
            'isPrefetch': 'false',
            'board_id': bid,
            'board_url': url,
            'field_set_key': 'react_grid_pin',
            'filter_section_pins': 'true', 
            'layout':'default',
            'page_size': PAGE_SIZE,
            'redux_normalize_feed': 'true',
            }

        if bookmark:
            options.update({
                'bookmarks': [bookmark],
            })

        i_len = len(images) - 1
        if i_len < 0:
            i_len = 0
        if section_slug:
            print('\r[...] Getting all images in this section: {}/{} ... [ {} / ? ]'
                .format(board_slug, section_slug, str(i_len)), end='')
        else:
            print('\r[...] Getting all images in this board: {} ... [ {} / ? ]'
                .format(board_slug, str(i_len)), end='')
        sys.stdout.flush()

        post_d = urllib.parse.urlencode({
            'source_url': url,
            'data': {
                'options': options,
                'context': {}
            },
            '_': int(time.time()*1000)
        }).replace('+', '').replace('%27', '%22') \
        .replace('%3A%22true%22', '%3Atrue').replace('%3A%22false%22', '%3Afalse')

        for t in RETRY_TIMEOUTS:
            try:
                if section_slug:
                    cookies = load_cookies(cookie_file)
                    r = IMGS_SESSION.get('https://www.pinterest.com/resource/BoardSectionPinsResource/get/'
                        , params=post_d, timeout=(t, t), cookies=cookies)
                else:
                    cookies = load_cookies(cookie_file)
                    r = IMGS_SESSION.get('https://www.pinterest.com/resource/BoardFeedResource/get/'
                        , params=post_d, timeout=(t, t), cookies=cookies)
                data = r.json()
                if data['resource_response']['data'] is None:
                    cprint(''.join([ HIGHER_YELLOW, '%s' % ('Failed. Retry after 30 seconds.') ]), attrs=BOLD_ONLY, end='\n' )
                    time.sleep(30)
                    IMGS_SESSION = get_session(2, proxies, cookie_file)
                    continue
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
                time.sleep(5)
                IMGS_SESSION = get_session(2, proxies, cookie_file)

        imgs_round = data['resource_response']['data']

        reach_lastest_pin = False
        if not arg_rescrape and sorted_api and (latest_pin != '0'):
            img_prev = 0
            on_hold_break = False
            for img_round_i, img in enumerate(imgs_round):
                if (isVideoExist(img)) or 'images' in img:
                    if img['id'].isdigit():
                        img_curr = img['id']
                        if img_prev and (int(img_curr) > int(img_prev)):
                            cprint(''.join([ HIGHER_YELLOW, '%s' % ('\n[W] This images list is not sorted(Due to user reorder), fallback to -rs for this list.\n\n') ]), attrs=BOLD_ONLY, end='' )
                            sorted_api = False
                            reach_lastest_pin = False
                            if on_hold_break:
                                imgs_round = data['resource_response']['data']
                            break
                        if latest_pin == img_curr:
                            imgs_round = imgs_round[:img_round_i]
                            reach_lastest_pin = True
                            on_hold_break = True
                        img_prev = img_curr
                    else:
                        cprint(''.join([ HIGHER_YELLOW, '%s' % ('\n[W] This images list is not sorted(Due to alphanumeric pin ID), fallback to -rs for this list.\n\n') ]), attrs=BOLD_ONLY, end='' )
                        sorted_api = False
                        reach_lastest_pin = False
                        imgs_round = data['resource_response']['data']
                        break
                else:
                    pass
        images.extend(imgs_round)
        if reach_lastest_pin:
            break_from_latest_pin = True
            break

        bookmark = data['resource']['options']['bookmarks'][0]

    if sorted_api:
        images = images[::-1]

    create_dir(save_dir)
    got_img = write_log(arg_timestamp_log, url_path, shortform, arg_img_only, arg_v_only, save_dir, images, None, arg_cut, break_from_latest_pin)

    if got_img:
        if break_from_latest_pin:
            img_total = len(images)
        else:
            img_total = len(images) - 1
            if img_total == 0:
                if ( (not arg_img_only and isVideoExist(images[0])) \
                    or (not arg_v_only and ('images' in images[0])) ):
                    img_total = 1
        if img_total == 0:
            print('\n[i] No {}item found.'.format('new ' if break_from_latest_pin else  ''))
            return

        if arg_max_count > 0 and img_total > arg_max_count:
            images = images[:arg_max_count]
            img_total = arg_max_count

        print( (' [' + plus_tag + '] Found {} {}image/video' + ('s' if img_total > 1 else '') ) 
            .format(img_total, 'new ' if break_from_latest_pin else  ''))
        print('Download into directory:  ' + save_dir.rstrip(os.sep) + os.sep)
    else:
        print('\n[i] No {}item found.'.format('new ' if break_from_latest_pin else  ''))
        return

    if arg_dry_run:
        print('\n[i] Dry run mode - would download {} files:'.format(img_total))
        for i, image in enumerate(images[:20]):
            if 'id' in image:
                img_url = ''
                if 'images' in image and image['images']:
                    img_url = image['images'].get('orig', {}).get('url', '')
                print('  {}. Pin {} {}'.format(i+1, image['id'], img_url[:60] if img_url else '(video)'))
        if img_total > 20:
            print('  ... and {} more'.format(img_total - 20))
        return

    if arg_thread_max < 1:
        arg_thread_max = None

    with ThreadPoolExecutor(max_workers = arg_thread_max) as executor:

        if arg_delay > 0:
            import itertools
            image_iter = iter(images)
            futures = set()
            for i, image in enumerate(image_iter):
                futures.add(executor.submit(download_img, image, save_dir, arg_force_update, arg_img_only, arg_v_only
                    , IMG_SESSION, V_SESSION, PIN_SESSION, proxies, cookie_file, arg_cut, arg_el, fs_f_max))
                if i < len(images) - 1:
                    time.sleep(arg_delay)
        else:
            futures = {executor.submit(download_img, image, save_dir, arg_force_update, arg_img_only, arg_v_only
                    , IMG_SESSION, V_SESSION, PIN_SESSION, proxies, cookie_file, arg_cut, arg_el, fs_f_max) for image in images}

        for index, f in enumerate(as_completed(futures)):
            printProgressBar(index + 1, len(images), prefix='[...] Downloading:'
                , suffix='Complete', length=50)

    printProgressBar(len(images), len(images), prefix='[' + done_tag + '] Downloaded:'
        , suffix='Complete   ', length=50)

    print()
