"""UI utilities - terminal output, colors, and progress display."""

import sys
import os
import platform

plat = platform.system().lower()
if ('window' in plat) or plat.startswith('win'):
    IS_WIN = True
    ANSI_CLEAR = '\r'
    ANSI_END_COLOR = ''
    ANSI_BLUE = ''
else:
    IS_WIN = False
    ANSI_CLEAR = '\r\x1b[0m\x1b[K'
    ANSI_END_COLOR = '\r\x1b[0m\x1b[K'
    ANSI_BLUE = '\x1b[1;44m'

from termcolor import cprint
import colorama
from colorama import Fore
colorama.init()

HIGHER_GREEN = Fore.LIGHTGREEN_EX
HIGHER_RED = Fore.LIGHTRED_EX
HIGHER_YELLOW = Fore.LIGHTYELLOW_EX
BOLD_ONLY = ['bold']

try:
    x_tag = '✖'
    done_tag = '✔'
    plus_tag = '➕'
    pinterest_logo = '🅿️'
    print(pinterest_logo, end=ANSI_CLEAR, flush=True)
except Exception:
    cprint(''.join([HIGHER_RED, '%s' % ('Please run `export PYTHONIOENCODING=utf-8;` to support Unicode.')]), attrs=BOLD_ONLY, end='\n')
    sys.exit(1)


def quit(msgs, exit=True):
    if not isinstance(msgs, list):
        msgs = [msgs]
    if exit:
        msgs[-1] += ' Abort.'
    for msg in msgs:
        if msg == '\n':
            print('\n')
        else:
            cprint(''.join([HIGHER_RED, '%s' % (msg)]), attrs=BOLD_ONLY, end='\n')
    if exit:
        sys.exit(1)


def printProgressBar(iteration, total, prefix='', suffix='', decimals=1, length=100, fill='#'):
    if total != 0:
        percent = ('{0:.' + str(decimals) + 'f}').format(100 * (iteration / float(total)))
        filledLength = int(length * iteration // total)
        bar = fill * filledLength + '-' * (length - filledLength)
        cprint(''.join([HIGHER_GREEN, '%s' % ('\r{} |{}| {}% {}'.format(prefix, bar, percent, suffix))]), attrs=BOLD_ONLY, end='')
        sys.stdout.flush()
