import os
import time
import traceback
import requests
from collections import OrderedDict

from .session import get_session, load_cookies
from .paths import get_output_file_path, create_dir
from .ui import cprint, quit, HIGHER_RED, BOLD_ONLY, x_tag, done_tag

RETRY_TIMEOUTS = (15, 30, 40, 50, 60)


def download_with_retry(session, url, file_path, proxies, cookie_file, session_ver=3, timeout_sequence=None):
    if timeout_sequence is None:
        timeout_sequence = RETRY_TIMEOUTS
    is_ok = False
    r = None
    for t in timeout_sequence:
        cookies = load_cookies(cookie_file)
        try:
            r = session.get(url, stream=True, timeout=(t, t), cookies=cookies)
            is_ok = True
            break
        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError):
            time.sleep(5)
            session = get_session(session_ver, proxies, cookie_file)
    if not is_ok or r is None or not r.ok:
        return False, session
    try:
        with open(file_path, 'wb') as f:
            for chunk in r:
                f.write(chunk)
        return True, session
    except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
        is_success = False
        for t in timeout_sequence:
            time.sleep(5)
            cookies = load_cookies(cookie_file)
            try:
                retry_session = get_session(session_ver, proxies, cookie_file)
                r = retry_session.get(url, stream=True, timeout=(t, t), cookies=cookies)
                with open(file_path, 'wb') as f:
                    for chunk in r:
                        f.write(chunk)
                is_success = True
                break
            except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError, requests.exceptions.ChunkedEncodingError):
                pass
        return is_success, session
    except OSError:
        return False, session


def isVideoExist(image):
    if ('videos' in image) and image['videos']:
        return 1
    elif 'story_pin_data' in image and image['story_pin_data'] and ('pages' in image['story_pin_data']):
        pg = image['story_pin_data']['pages']
        if (len(pg) > 0) and ('blocks' in pg[0]):
            blocks = pg[0]['blocks']
            if len(blocks) > 0 and 'video' in blocks[0] and ('video_list' in blocks[0]['video']):
                return 2
    return 0


def download_img(image, save_dir, arg_force_update, arg_img_only, arg_v_only, IMG_SESSION, V_SESSION, PIN_SESSION, proxies, cookie_file, arg_cut, arg_el, fs_f_max, arg_quality='orig'):

    try:
        if 'id' not in image:
            print('\n\nSkip no id\n\n')
            return
        image_id = image['id']

        human_fname = ''
        if ('grid_title' in image) and image['grid_title']:
            human_fname = '_' + image['grid_title']
        if ('closeup_unified_description' in image) and image['closeup_unified_description'] and image['closeup_unified_description'].strip():
            human_fname = '_'.join((human_fname, image['closeup_unified_description'].strip()))
        elif ('description' in image) and image['description'] and image['description'].strip():
            human_fname = '_'.join((human_fname, image['description'].strip()))
        if ('created_at' in image) and image['created_at']:
            img_created_at = image['created_at'].replace(':', '').replace(' +0000', '')
            img_created_at_l = img_created_at.split(' ')
            if len(img_created_at_l) == 5:
                img_created_at = ''.join(img_created_at_l[1:4])
            human_fname = '_'.join([human_fname, img_created_at])

        if not arg_v_only and ('images' in image):
            if arg_quality != 'orig' and arg_quality in image.get('images', {}):
                url = image['images'][arg_quality]['url']
            elif 'orig' in image.get('images', {}):
                url = image['images']['orig']['url']
            else:
                url = image['images'][list(image['images'].keys())[-1]]['url']

            file_path = get_output_file_path(url, arg_cut, fs_f_max, image_id, human_fname, save_dir)
            if arg_el:
                file_path = '\\\\?\\' + os.path.abspath(file_path)

            if not os.path.exists(file_path) or arg_force_update:
                success, IMG_SESSION = download_with_retry(IMG_SESSION, url, file_path, proxies, cookie_file, session_ver=3)
                if not success:
                    cprint(''.join([ HIGHER_RED, '%s %s %s %s%s' % ('\n[' + x_tag + '] Download this image at'
                    , file_path, 'failed URL:', url, '\n') ]), attrs=BOLD_ONLY, end='' )
                    cprint(''.join([ HIGHER_RED, '%s' % ('\n[e1] You may want to delete this image manually and retry later(with -rs or try with single pin '
                    + ('https://www.pinterest.com/pin/' + repr(image['id']).strip("'")  ) + ').\n\n') ]), attrs=BOLD_ONLY, end='' )
                    return

                else:
                    imgDimens = []
                    imgDimensD = {}
                    for ik, iv in image['images'].items():
                        if 'x' in ik:
                            imgDimens.append(iv['width'])
                            imgDimensD[iv['width']] =  iv['url']
                    if imgDimens:
                        imgDimens.sort(key=int)
                        url = imgDimensD[int(imgDimens[-1])]

                        file_path = get_output_file_path(url, arg_cut, fs_f_max, image_id, human_fname, save_dir)
                        if arg_el:
                            file_path = '\\\\?\\' + os.path.abspath(file_path)

                        if not os.path.exists(file_path) or arg_force_update:
                            success, IMG_SESSION = download_with_retry(IMG_SESSION, url, file_path, proxies, cookie_file, session_ver=3)
                            if not success:
                                cprint(''.join([ HIGHER_RED, '%s %s %s %s%s' % ('\n[' + x_tag + '] Retried this image at'
                                    , file_path, 'failed :', url, '\n') ]), attrs=BOLD_ONLY, end='' )
                                cprint(''.join([ HIGHER_RED, '%s' % ('\n[e2] You may want to delete this image manually and retry later.\n\n') ]), attrs=BOLD_ONLY, end='' )
                        else:
                            pass

        else:
            pass

        if not arg_img_only:
            video_type = isVideoExist(image)
            if video_type == 0:
                return

            v_pin_id = image['id']
            image = get_pin_info(v_pin_id, None, None, None, False, False, None, None, None, None, IMG_SESSION, V_SESSION, PIN_SESSION, proxies, cookie_file, True)
            if not image:
                cprint(''.join([ HIGHER_RED, '%s %s%s' % ('\n[' + x_tag
                    + '] Get this video pin id failed :', v_pin_id, '\n') ]), attrs=BOLD_ONLY, end='' )
                return
            if video_type == 1:
                v_d = image['videos']['video_list']
            elif video_type == 2:
                v_d_unsort = image['story_pin_data']['pages'][0]['blocks'][0]['video']['video_list']
                v_d = OrderedDict(sorted(v_d_unsort.items(), key=lambda t: t[0]))
            vDimens = []
            vDimensD = {}
            for v_format, v_v in v_d.items():
                if 'url' in v_v and v_v['url'].endswith('mp4'):
                    vDimens.append(v_v['width'])
                    vDimensD[v_v['width']] =  v_v['url']
            if vDimens:
                vDimens.sort(key=int)
                vurl = vDimensD[int(vDimens[-1])]

                file_path = get_output_file_path(vurl, arg_cut, fs_f_max, image_id, human_fname, save_dir)

                if arg_el:
                    file_path = '\\\\?\\' + os.path.abspath(file_path)

                if not os.path.exists(file_path) or arg_force_update:
                    success, V_SESSION = download_with_retry(V_SESSION, vurl, file_path, proxies, cookie_file, session_ver=4)
                    if not success:
                        cprint(''.join([ HIGHER_RED, '%s %s %s %s%s' % ('\n[' + x_tag + '] Download this video at'
                            , file_path, 'failed :', vurl, '\n') ]), attrs=BOLD_ONLY, end='' )
                        cprint(''.join([ HIGHER_RED, '%s' % ('\n[e3] You may want to delete this video manually and retry later.\n\n') ]), attrs=BOLD_ONLY, end='' )

    except Exception:
        print()
        return quit(traceback.format_exc())
