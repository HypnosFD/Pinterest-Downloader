import requests
from fake_useragent import UserAgent
from http.cookies import SimpleCookie
from requests.cookies import cookiejar_from_dict

ua = UserAgent()
UA = ua.chrome

VER = (None, '977943c', '4c8c36f')


def load_cookies(cookie_file):
    try:
        with open(cookie_file, encoding="utf-8") as f:
            rawdata = f.read()
        my_cookie = SimpleCookie()
        my_cookie.load(rawdata)
        return cookiejar_from_dict({key: morsel.value for key, morsel in my_cookie.items()})
    except (FileNotFoundError, OSError, TypeError):
        return None


def create_sessions(proxies, cookie_file):
    return {
        'page': get_session(0, proxies, cookie_file),
        'feed': get_session(2, proxies, cookie_file),
        'image': get_session(3, proxies, cookie_file),
        'video': get_session(4, proxies, cookie_file),
    }


def get_session(ver_i, proxies, cookie_file):
    s = requests.Session()
    s.proxies = proxies

    cookies = load_cookies(cookie_file)

    try:
        s.cookies = cookies
    except (TypeError, ValueError):
        pass

    csrf_token = s.cookies.get('csrftoken', '') if s.cookies else ''

    if ver_i == 0:
        s.headers = {
            'User-Agent': UA,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
            'Connection': 'keep-alive'
        }
    elif ver_i == 3:
        s.headers = {
            'User-Agent': UA,
            'Accept': 'image/webp,*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.pinterest.com/',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'Trailers'
        }

    elif ver_i == 4:
        s.headers = {
            'User-Agent': UA,
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.pinterest.com',
            'DNT': '1',
            'Referer': 'https://www.pinterest.com/',
            'Connection': 'keep-alive',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

    else:
        s.headers = {
            'User-Agent': UA,
            'Accept': 'application/json, text/javascript, */*, q=0.01',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.pinterest.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': csrf_token,
            'X-APP-VERSION': VER[ver_i],
            'X-Pinterest-AppState': 'active',
            'X-Pinterest-PWS-Handler': 'www/[username]/[slug]/[section_slug].js',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'Trailers'
        }

    return s
