"""Path handling utilities for Pinterest downloader."""

import sys
import os
import re
from pathlib import PurePath
from termcolor import cprint

from .ui import IS_WIN, HIGHER_RED, BOLD_ONLY


def sanitize_fname(name):
    # Replace underscores with spaces first (Pinterest uses _ as word separator)
    name = name.replace('_', ' ')
    # Remove emojis and non-ASCII characters (Cyrillic, CJK, etc.)
    name = re.sub(r'[^\x00-\x7F]+', '', name)
    # Replace common problematic characters
    name = name.replace('&', 'and')
    name = name.replace('#', '')
    name = name.replace('%', '')
    name = name.replace('@', '')
    name = name.replace('!', '')
    name = name.replace('~', '')
    name = name.replace('`', '')
    name = name.replace('+', '')
    name = name.replace('=', '')
    name = name.replace('-', ' ')
    name = name.replace('.', ' ')
    name = name.replace(',', ' ')
    name = name.replace('{', '').replace('}', '')
    name = name.replace('[', '').replace(']', '')
    name = name.replace('(', '').replace(')', '')
    # Collapse all whitespace and strip
    name = re.sub(r'\s+', ' ', name).strip()
    # Limit to 80 characters to keep filenames short and cross-platform safe
    if len(name) > 80:
        name = name[:80].rstrip()
    return name


def sanitize(path):
    # trim multiple whitespaces # ".." is the responsibilities of get max path

    # Use PurePath instead of os.path.basename  https://stackoverflow.com/a/31273488/1074998 , e.g.:
    #>>> PurePath( '/home/iced/..'.replace('..', '') ).parts[-1] # get 'iced'
    #>>> os.path.basename('/home/iced/..'.replace('..', '')) # get empty ''
    # Ensure .replace('..', '') is last replacement before .strip() AND not replace back to dot '.'
    # https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file
    
    # [todo:0] Handle case sensitive and reserved file names in Windows like Chrome "Save page as" do
    # For portable to move filename between linux <-> win, should use IS_WIN only (but still can't care if case sensitive filename move to case in-sensitive filesystem). 
    # IS_WIN:
    path = path.replace('<', '').replace('>', '').replace('"', '\'').replace('?', '').replace('*', '').replace('/', '_').replace('\\', '_').replace('|', '_').replace(':', '_').replace('.', '_').strip()
    # Linux:
    #path.replace('/', '|').replace(':', '_').replace('.', '_').strip()

    # Put this after replace patterns above bcoz 2 distinct spaces may merge together become multiple-spaces, e.g. after ' ? ' replace to '  '
    # If using .replace('  ', ' ') will only replace once round, e.g. '    ' become 
    path = ' '.join(path.split()) 

    p = PurePath( path )

    if p.parts:
        return p.parts[-1]
    else:
        return ''

# The filesystem limits is 255(normal) , 242(docker) or 143((eCryptfs) bytes
# So can't blindly [:] slice without encode first (which most downloaders do the wrong way)
# And need decode back after slice
# And to ensure mix sequence byte in UTF-8 and work
#, e.g. abc𪍑𪍑𪍑
# , need try/catch to skip next full bytes of "1" byte ascii" OR "3 bytes 我" or "4 bytes 𪍑"
# ... by looping 4 bytes(UTF-8 max) from right to left
# HTML5 forbid UTF-16, UTF-16/32 not encourage to use in web page
# So only encode/decode in utf-8
# https://stackoverflow.com/questions/13132976
# https://stackoverflow.com/questions/50385123
# https://stackoverflow.com/questions/11820006

def get_max_path(arg_cut, fs_f_max, fpart_excluded_immutable, immutable):
    #print('before f: ' + fpart_excluded_immutable)
    if arg_cut >= 0:
        fpart_excluded_immutable = fpart_excluded_immutable[:arg_cut]
    if immutable:
        # immutable shouldn't limit to 1 byte(may be change next time or next project), so need encode also
        immutable_len = len(immutable.encode('utf-8'))
    else:
        immutable_len = 0

    space_remains = fs_f_max - immutable_len
    if space_remains < 1:
        return '' # No more spaces to trim(bcoz directories name too long), so only shows PinID.jpg

    # range([start], stop[, step])
    # -1 step * 4 loop = -4, means looping 4 bytes(UTF-8 max) from right to left
    for gostan in range(space_remains, space_remains - 4, -1):
        try:
            fpart_excluded_immutable = fpart_excluded_immutable.encode('utf-8')[: gostan ].decode('utf-8')
            break # No break still same result, but waste
        except UnicodeDecodeError:
            pass #print('Calm down, this is normal: ' + str(gostan) + ' f: ' + fpart_excluded_immutable)
    #print('after f: ' + fpart_excluded_immutable)
    # Last safety resort, in case any bug:
    fpart_excluded_immutable_base = sanitize ( fpart_excluded_immutable )
    if fpart_excluded_immutable_base != fpart_excluded_immutable.strip(): # Original need strip bcoz it might cut in space
        cprint(''.join([ HIGHER_RED, '\n[! A] Please report to me which Link/scenario it print this log.\
            Thanks:\n{} # {} # {} # {} # {}\n\n'
            .format(arg_cut, fs_f_max, repr(fpart_excluded_immutable), repr(fpart_excluded_immutable_base), immutable) ]), attrs=BOLD_ONLY, end='' )  
    return fpart_excluded_immutable_base

def get_output_file_path(url, arg_cut, fs_f_max, image_id, human_fname, save_dir):

    pin_id_str = sanitize(str(image_id))
    basename = os.path.basename(url) # basename not enough to handle '..', but will sanitize later
    # throws ValueError is fine bcoz it's not normal

    # Test case need consider what if multiple dots in basename
    #human_fname_unused = '.'.join(basename.split('.')[:-1]) # this project already has human_fname, but other project can use this
    ext = basename.split('.')[-1]

    ext = sanitize(ext)
    if not ext.strip(): # Ensure add hard-coded extension to avoid empty id and leave single dot in next step
        ext = 'unknown'
    # Currently not possible ..jpg here bcoz above must single '.' do not throws
    # , even replace ..jpg to _.jpg is fine, just can't preview in explorer only 
    immutable = sanitize( pin_id_str + '.' +  ext )

    fpart_excluded_ext_before  = sanitize( human_fname )
    #print( 'get output f:' + repr(fpart_excluded_ext_before) )

    # [DEPRECATED, now always use extended length which apply to single component instead of full path]
    #if IS_WIN: # Windows MAX_PATH 260 is full path not single component (https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file , https://docs.microsoft.com/en-us/windows/win32/fileio/naming-a-file#maximum-path-length-limitation) 
    #    immutable_file_path = os.path.abspath( os.path.join(save_dir, '{}'.format( immutable)) )
    #    fpart_excluded_ext = get_max_path(arg_cut, fs_f_max, fpart_excluded_ext_before
    #        , immutable_file_path)
    #else:    
    fpart_excluded_ext = get_max_path(arg_cut, fs_f_max, fpart_excluded_ext_before
            , immutable)
    if fpart_excluded_ext:
        if fpart_excluded_ext_before == fpart_excluded_ext: # means not truncat
            # Prevent confuse when trailing period become '..'ext and looks like '...'
            if fpart_excluded_ext[-1] == '.':
                fpart_excluded_ext = fpart_excluded_ext[:-1]
        else: # Truncated
            # No need care if two/three/... dots, overkill to trim more and loss information
            if fpart_excluded_ext[-1] == '.':
                fpart_excluded_ext = fpart_excluded_ext[:-1]

            #if IS_WIN: # [DEPRECATED] Now always use -el
            #    # Need set ... here, not abspath below which trimmed ... if ... at the end.
            #    # Also ensures sanitize replace single '.', not '..' which causes number not equal after added ... later
            #    immutable = sanitize( pin_id_str + '....' +  ext )
            #    immutable_file_path = os.path.abspath( os.path.join(save_dir, '{}'.format( immutable)) )
            #    fpart_excluded_ext = get_max_path(arg_cut, fs_f_max, fpart_excluded_ext_before
            #            , immutable_file_path)
            #else:
            fpart_excluded_ext = get_max_path(arg_cut, fs_f_max, fpart_excluded_ext
                , '...' + immutable)

            fpart_excluded_ext = fpart_excluded_ext + '...'

    # To make final output path consistent with IS_WIN's abspath above, so also do abspath here:
    # (Please ensure below PurePath's file_path checking is using abspath if remove abspath here in future)
    file_path = os.path.abspath( os.path.join(save_dir, '{}'.format( pin_id_str + fpart_excluded_ext + '.' +  ext)) )
    #if '111' in file_path:
    #    print('last fp: ' + file_path + ' len: ' + str(len(file_path.encode('utf-8'))))
    try:
        # Note this is possible here if only . while the rest is empty, e.g. './.'
        # But better throws and inform me if that abnormal case.
        if PurePath(os.path.abspath(save_dir)).parts[:] != PurePath(file_path).parts[:-1]:
            cprint(''.join([ HIGHER_RED, '\n[! B] Please report to me which Link/scenario it print this log.\
                Thanks: {} # {} # {} # {} # {} \n\n'
                .format(arg_cut, fs_f_max, pin_id_str + fpart_excluded_ext + '.' +  ext, save_dir, file_path) ]), attrs=BOLD_ONLY, end='' )  
            file_path = os.path.join(save_dir, '{}'.format( sanitize(pin_id_str + fpart_excluded_ext + '.' +  ext)))
            if PurePath(os.path.abspath(save_dir)).parts[:] != PurePath(file_path).parts[:-1]:
                cprint(''.join([ HIGHER_RED, '\n[! C] Please report to me which Link/scenario it print this log.\
                    Thanks: {} # {} # {} # {} # {} \n\n'
                    .format(arg_cut, fs_f_max, pin_id_str + fpart_excluded_ext + '.' +  ext, save_dir, file_path) ]), attrs=BOLD_ONLY, end='' )  
                raise RuntimeError('Path verification failed')
    except IndexError:
        cprint(''.join([ HIGHER_RED, '\n[! D] Please report to me which Link/scenario it print this log.\
            Thanks: {} # {} # {}\n\n'
            .format(arg_cut, fs_f_max, pin_id_str + fpart_excluded_ext + '.' +  ext) ]), attrs=BOLD_ONLY, end='' )  
        raise
    #print('final f: ' + file_path)
    return file_path

def create_dir(save_dir):

    try:
        if IS_WIN:
            os.makedirs('\\\\?\\' + os.path.abspath(save_dir))
        else:
            os.makedirs(save_dir)
    except FileExistsError: # Check this first to avoid OSError cover this
        pass # Normal if re-download
    except OSError: # e.g. File name too long 

        # Only need to care for individual path component
        #, i.e. os.statvfs('./').f_namemax = 255(normal fs), 242(docker) or 143(eCryptfs) )
        #, not full path( os.statvfs('./').f_frsize - 1 = 2045)
        # Overkill seems even you do extra work to truncate path, then what if user give arg_dir at
        # ... 2045th path? how is it possible create new dir/file from that point?
        # So only need to care for individual component 
        #... which max total(estimate) is uname 100 + (boardname 50*4)+( section 50*3) = ~450 bytes only.
        # Then add max file 255 bcome 705, still far away from 2045th byte(or 335 4_bytes utf-8)
        # So you direct throws OSError enough to remind that user don't make insane fs hier

        cprint(''.join([ HIGHER_RED, '%s' % ('\nIt might causes by too long(2045 bytes) in full path.\
        You may want to to use -d <other path> OR -c <Maximum length of folder & filename>.\n\n') ]), attrs=BOLD_ONLY, end='' )  
        raise