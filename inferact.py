#!/usr/bin/python
# -*- coding: utf-8 -*-

__nfr__     = 'inferact'
__version__ = '0.4.9.15 prealpha'
__website__ = 'https://sourceforge.net/projects/inferact/'
__about__   = __nfr__.capitalize()+' (or nfer for short) is an unproblematic tagging utility.'

DEBUG_PERFORMANCE = False

#-------------------------------------------------------------------------------
# IMPORTS, INITS, GLOBALS
#-------------------------------------------------------------------------------

try:
    import win_unicode_console # https://pypi.python.org/pypi/win_unicode_console
    win_unicode_console.enable() # enable Unicode support
except:
    pass

TECHNICAL_INFO = False
debug = False
skippy = False # display "skipped"/"cancelled" etc. messages
post_subprocess_delay = 0.0001 # open subprocess seems to be a race condition

if DEBUG_PERFORMANCE:
    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()

from terminalsize import get_terminal_size
from nfr_similar import *
from math import sqrt
import random, sys, os
from hashlib import md5
try:
    import collage
except:
    pass
from PIL import ImageGrab # for clipboard image similarity search

if os.path.isfile('magics.csv'):
    from whatype import Whatype # get filetype from file header
    WTlib = Whatype('magics.csv') # Uses default magics.csv shipped with the library
else:
    WTlib = None

nfr_title = '  [ '+__nfr__+' '+__version__+' ]'
def set_console_title(title):
    if os.name == 'nt': # Windows
        os.system('title '+title)
    elif os.name in ('posix', 'mac'): # Linux or Darwin
        sys.stdout.write('\x1b]2;'+title+'\x07')

try:
    from colorama import Fore, Style, init, deinit, reinit, Back
    TINT    = Fore.CYAN
    ERRORT  = Fore.RED
    BERRORT = Style.BRIGHT+Fore.RED
    DULL    = Style.RESET_ALL
    BDULL   = Style.RESET_ALL+Style.BRIGHT
    BRIGHT  = Style.BRIGHT
    NORMAL  = Style.NORMAL
    BLIME   = Style.BRIGHT+Fore.GREEN
    def tint(s, tint=None):
        if tint is None:
            return TINT+s+DULL
        else:
            tint = tint.upper()
            if not tint in ('RED','GREEN','YELLOW','BLUE','MAGENTA','CYAN','WHITE'):
                return TINT+s+DULL
            else:
                return getattr(Fore, tint)+s+DULL
    def bright_tint(s):
        return tint(BRIGHT+s+NORMAL)
    btint = bright_tint
    def error_bright_tint(s):
        return ERRORT+BRIGHT+s+DULL
    def error_tint(s):
        return ERRORT+s+DULL
    error_btint = error_bright_tint

    init(wrap=True)
    def rawc_input(s): # TEMPORARILY DISABLES COLORAMA'S WRAPPING FOR AUTOCOMPLETION
        #deinit()
        #win_unicode_console.raw_input.stdin_decode('utf-8')
        out = raw_input(s)
        #reinit()
        return out
except:
    TINT = ERRORT = BERRORT = DULL = BDULL = BRIGHT = NORMAL = BLIME = ''
    tint = bright_tint = error_bright_tint = error_tint = error_btint = lambda x: x # does nothing
    rawc_input = raw_input

try:
    import maya # https://github.com/kennethreitz/maya
except:
    pass

def print_exception():
    print sys.exc_info()

def sorted_unique_average_bright(seq, reverse=False): # TO-FIX!!!!!!!!!!!!!!!!!!
    UAs = sorted_unique_amount(seq, reverse=reverse)
    if not UAs: return UAs
    average = float(sum([UA[1] for UA in UAs])) / len(UAs)
    for i,UA in enumerate(UAs):
        UAs[i] = BRIGHT+UA[0]+NORMAL+'('+str(UA[1])+')' if UA[1] > average else UA[0]
    return UAs

import re
def quasi_markup(s):
    s = s.split('\n')
    for i,ln in enumerate(s):
        if '___' in ln:
            ln = re.sub(r'___([^\ _].*?)___', BRIGHT+TINT+r'\g<1>'+DULL, ln)        # ___BRIGHT-TINTED-TEXT___
        if '__' in ln:
            ln = re.sub( r'__([^\ _].*?)__', TINT+r'\g<1>'+Fore.RESET, ln)          # __TINTED-TEXT__
        if '_' in ln:
            ln = re.sub(  r'_([^\ _].*?)_', BRIGHT+r'\g<1>'+NORMAL, ln)             # _BRIGHT-TEXT_
        if '***' in ln:
            ln = re.sub(r'\*\*\*([^\ \*].*?)\*\*\*', BRIGHT+TINT+r'\g<1>'+DULL, ln) # ***BRIGHT-TINTED-TEXT***
        if '**' in ln:
            ln = re.sub(  r'\*\*([^\ \*].*?)\*\*', TINT+r'\g<1>'+Fore.RESET, ln)    # **TINTED-TEXT**
        if -1 != ln.find('<<<') < ln.find('>>>'):
            ln = re.sub(r'<<<([^\ \*].*?)>>>', BERRORT+r'\g<1>'+DULL, ln)           # <<<BRIGHT-ERROR-TEXT>>>
        if -1 != ln.find('<<') < ln.find('>>'):
            ln = re.sub(  r'<<([^\ \*].*?)>>', ERRORT+r'\g<1>'+Fore.RESET, ln)      # <<ERROR-TEXT>>
        if '*' in ln:
            ln = re.sub(    r'\*([^\ \*].*?)\*', BRIGHT+r'\g<1>'+NORMAL, ln)        # *BRIGHT-TEXT*
        if '---' in ln:
            ln = re.sub(r'([\-]){3,}', ' '+('-'*(get_terminal_size()[0]-2)), ln)    # ---LINE
        if '`' in ln:
            ln = re.sub(r'`([^\ `].*?)`', BRIGHT+TINT+r'\g<1>'+DULL, ln)            # `BRIGHT-TINTED-TEXT`
        if ln.startswith('# '):                                                     # # CENTERED-TEXT
            ln = center_text(ln[2:])
        s[i] = ln
    s = '\n'.join(s)
    return s

def tint_special_chars(tag_string): # : / _
    words = tag_string.split()
    for i,s in enumerate(words):
        if '/' in s:
            s = s.replace('/', TINT+'/'+DULL)
        if '_' in s:
            s = s.replace('_', BRIGHT+'_'+NORMAL)
        if ':' in s:
            s = s.split(':')
            s = BRIGHT+TINT+s[0]+NORMAL+':'+DULL + (TINT+':'+DULL).join(s[1:])
        words[i] = s[:]
    return ' '.join(words)

def cprint(s, newline=True, markup=False):
    if '[!]' in s:
        s = s.replace('[!]', ERRORT+'[!]',1)+DULL
    elif '[+]' in s:
        s = s.replace('[+]', Fore.GREEN+'[+]',1)+DULL
    elif '[-]' in s:
        s = s.replace('[-]', ERRORT+'[-]',1)+DULL
    elif '[Error' in s:
        s = s.replace('[Error', ERRORT+'[Error',1)+DULL
    if markup:
        s = quasi_markup(s)
    if newline:
        print s
    else:
        sys.stdout.write(s)
        #print s,

def tryint(s):
    try:
        return int(s)
    except:
        return s
def alphanum_key(s):
    """ Turn a string into a list of string and number chunks.
        "z23a" -> ["z", 23, "a"]
    """
    return [ tryint(c) for c in re.split('([0-9]+)', s) ]
def sort_nicely(l, reverse=False): # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
    """ Sort the given list in the way that humans expect.
    """
    l.sort(key=alphanum_key, reverse=reverse)
def M_alphanum_key(M2):
    return [ tryint(c) for c in re.split('([0-9]+)', M2.filepath if M2.filepath else '') ]
def M2_sort_nicely(metadata_list, reverse=False): # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-in-python-based-on-an-attribute-of-the-objects
    metadata_list.sort(key=M_alphanum_key, reverse=reverse)

import ntpath # http://stackoverflow.com/a/8384788
import datetime
from time import sleep
try: from send2trash import send2trash # https://stackoverflow.com/questions/3628517/how-can-i-move-file-into-recycle-bin-trash-on-different-platforms-using-pyqt4
except: raise ImportError(' [!] send2trash is not installed')
import shutil
try: import xerox # https://github.com/kennethreitz/xerox
except: raise ImportError(' [!] xerox is not installed')

import subprocess
def run_with_default_app(filepath):
    try:
        if sys.platform.startswith('darwin'):
            subprocess.call(('open', filepath))
        elif os.name == 'nt':
            if filepath[0] == ':':
                os.system(filepath[1:])
            else:
                os.startfile(filepath)
        elif os.name == 'posix':
            subprocess.call(('xdg-open', filepath))
    except:
        print_exception()

clear = lambda: os.system('cls' if os.name == 'nt' else 'clear') # clears console (cross-system)

try: from buzhug import TS_Base # http://buzhug.sourceforge.net/
except: raise ImportError(' [!] buzhug is not installed')
buzhug_db, buzhug_alias_db, buzhug_variant_db = None, None, None

import readline, glob # https://docs.python.org/2/library/readline.html # https://docs.python.org/2/library/glob.html
class Complete(object):
    def __init__(self, cmds=list()):
        self.cmds = sorted(cmds)
        #readline.set_completer_delims(' \t\n\;')
        readline.set_completer_delims(' \\/;')
        readline.parse_and_bind('tab: complete')
        self.options = None
    def set_custom(self, cmds=list()):
        self.cmds = sorted(cmds)
    def custom(self, text, state): # https://stackoverflow.com/questions/187621/how-to-make-a-python-command-line-program-autocomplete-arbitrary-things-not-int
        options = [i for i in self.cmds if i.startswith(text)]
        if state < len(options):
            self.options = options[:]
            return options[state]
        else:
            #self.options = None
            return None
    def path(self, text, state): # https://stackoverflow.com/questions/6656819/filepath-autocompletion-using-users-input
        return (glob.glob(text+'*')+[None])[state]
complete = Complete()

from nfr_basic import *
pprc = CrudeProgress(custom=('[# ]'),width=22)
#pprc = CrudeProgress()
from nfr_files import * # file operations & hashing

# !!!!!!!!!!!!! os.getcwd() & os.path.abspath(__file__) can be called only in __main__  otherwise pyinstaller references to temp-installation dir (MEI_) !!!!!!!!!
OLD_WORKING_DIR = os.getcwd()
# Change the scripts working directory to the script's own directory # http://stackoverflow.com/a/1432949
SCRIPT_FILEPATH = os.path.abspath(__file__)
SCRIPT_DIR = os.path.dirname(SCRIPT_FILEPATH)
HOME_DIR = os.path.expanduser('~')
DBA_NAME = ''
def show_expandvars_nfr_only():
    cprint(ansi_definition(TINT+' URL-ABBREVIATIONS: '+DULL, '%nfr% %cwd% %home% %db%\n'))
def expandvars_nfr_only(filepath):
    if filepath.count('%')<2:
        return filepath
    ret = filepath.replace('%nfr%',SCRIPT_DIR).replace('%nfer%',SCRIPT_DIR).replace('%inferact%',SCRIPT_DIR).replace('%root%',SCRIPT_DIR)
    ret = ret.replace('%NFR%',SCRIPT_DIR).replace('%NFER%',SCRIPT_DIR).replace('%INFERACT%',SCRIPT_DIR).replace('%ROOT%',SCRIPT_DIR)
    ret = ret.replace('%SCRIPT%',os.getcwd()).replace('%script%',os.getcwd())
    ret = ret.replace('%CWD%',os.getcwd()).replace('%cwd%',os.getcwd())
    ret = ret.replace('%HOME%',HOME_DIR).replace('%USER%',HOME_DIR)
    ret = ret.replace('%home%',HOME_DIR).replace('%user%',HOME_DIR)
    ret = ret.replace('%OLD_WORKING_DIR%',OLD_WORKING_DIR).replace('%old_working_dir%',OLD_WORKING_DIR).replace('%OWD%',OLD_WORKING_DIR).replace('%owd%',OLD_WORKING_DIR)
    ret = ret.replace('%DB%',DBA_NAME).replace('%DBA%',DBA_NAME)
    ret = ret.replace('%db%',DBA_NAME).replace('%dba%',DBA_NAME)
    return ret
def format_path_nt(filepath): # overwriting from nfr_files.py, adapted to nfr (extended functionality, yay!)
    #filepath = os.path.normcase(filepath) # converts path to lowercase on case-insensitive systems
    while filepath and filepath[0]=='"' and filepath[-1]=='"': filepath = filepath[1:-1]
    while filepath and filepath[0]=="'" and filepath[-1]=="'": filepath = filepath[1:-1]
    if filepath.startswith('idea:'):
        filepath = os.path.expandvars(expandvars_nfr_only(filepath[5:]))
        return 'idea:'+os.path.normpath(filepath)
    return os.path.normpath(os.path.expandvars(expandvars_nfr_only(filepath))) # path is not OS poratble!
def format_path_unix(filepath): # overwriting from nfr_files.py, adapted to nfr (extended functionality, yay!)
    while filepath and filepath[0]=='"' and filepath[-1]=='"': filepath = filepath[1:-1]
    while filepath and filepath[0]=="'" and filepath[-1]=="'": filepath = filepath[1:-1]
    if filepath.startswith('idea:'):
        filepath = os.path.expandvars(expandvars_nfr_only(filepath[5:]))
        return 'idea:'+os.path.normpath(filepath)
    return os.path.normpath(os.path.expandvars(expandvars_nfr_only(filepath))) # path is not OS poratble!
format_path = format_path_nt if os.name == 'nt' else format_path_unix
def expandvars_nfr(filepath):
    return os.path.expandvars(expandvars_nfr_only(filepath))
# !!!!!!!!!!!!! EOM

def path_is_buzhug_db(path):
    filelist = ('__defaults__','__del_rows__','__id__','__info__','__version__','_id_pos','added','filepath','hash','modified','tags','phash')
    folderlist = ('buzhug_alias_db','buzhug_variant_db')
    for folder in folderlist:
        if not os.path.exists(os.path.join(path, folder)):
            return False
    for file in filelist:
        if not os.path.isfile(os.path.join(path, file)):
            return False
    return True

def get_buzhug_db_paths(paths):
    dbList = list()
    for path in filter(None,paths):
        #path = format_path(path) # WINDOWS
        found = [ os.path.join(root,dir)
                  for root,dirs,files in os.walk(path)
                  for dir in dirs if path_is_buzhug_db(os.path.join(root,dir)) ]
        if found:
            dbList.extend(found)
    if dbList:
        for i,path in enumerate(dbList):
            if path.startswith('.\\'): dbList[i] = path[2:] # remove ".\" from relative paths
        dbList.sort()
        return dbList
    else:
        return None

def motd_color_parser(s):
    DULL = Style.RESET_ALL
    BRIGHT = Style.BRIGHT
    NORMAL = Style.NORMAL
    RED = Fore.RED
    LRED = Style.BRIGHT+Fore.RED
    GREEN = Fore.GREEN
    LGREEN = Style.BRIGHT+Fore.GREEN
    YELLOW = Fore.YELLOW
    LYELLOW = Style.BRIGHT+Fore.YELLOW
    BLUE = Fore.BLUE
    LBLUE = Style.BRIGHT+Fore.BLUE
    MAGENTA = Fore.MAGENTA
    LMAGENTA = Style.BRIGHT+Fore.MAGENTA
    CYAN = Fore.CYAN
    LCYAN = Style.BRIGHT+Fore.CYAN
    WHITE = Fore.WHITE
    LWHITE = Style.BRIGHT+Fore.WHITE
    LBLACK = Style.BRIGHT+Fore.BLACK
    char_color_codes = {
                    'w': WHITE,
                    #'W': BWHITE,
                    'r': RED,
                    #'R': BRED,
                    'g': GREEN,
                    #'G': BGREEN,
                    'b': BLUE,
                    #'B': BBLUE,
                    'c': CYAN,
                    #'C': BCYAN,
                    'm': MAGENTA,
                    #'M': BMAGENTA,
                    'y': YELLOW,
                    #'Y': BYELLOW,
                    'W': LWHITE,
                    'R': LRED,
                    'G': LGREEN,
                    'B': LBLUE,
                    'C': LCYAN,
                    'M': LMAGENTA,
                    'Y': LYELLOW,
                    'L': BRIGHT,
                    'x': DULL
                   }
    chars, colors = part(s,'@color-matrix:')
    colored = list()
    for i,c in enumerate(chars):
        try:
            colored.append(char_color_codes[colors[i]])
        except: pass
        colored.append(c)
    return ''.join(colored)


from urlparse import urlparse # https://stackoverflow.com/questions/827557/how-do-you-validate-a-url-with-a-regular-expression-in-python
remote_schemes = tuple('idea ftp gopher hdl http https imap mailto mms news nntp prospero rsync rtsp rtspu sftp shttp sip sips snews svn svn+ssh telnet wais'.split())
local_schemes  =      ('file', '')

from collections import namedtuple # http://stackoverflow.com/a/2970722
#-------------------------------------------------------------------------------
#                                          0   1        2    3    4     5        6     7
M2tuple = namedtuple('metadata','rec filepath hash tags added modified phash')
#-------------------------------------------------------------------------------

def rec2M2(rec): # converts a database record to a M2 tuple
    return M2tuple(rec, rec.filepath, rec.hash, rec.tags, rec.added, rec.modified, rec.phash)
def M2changed(M2):
    return M2[0].filepath != M2[1] or M2[0].hash != M2[2] or set(M2[0].tags.split()) != set(M2[3].split()) or M2[0].added != M2[4] or M2[0].modified != M2[5] or M2[0].phash != M2[6]
# GETTERS:
# M2.rec
# M2.filepath
# M2.hash
def getM2tags(M2): return set(M2[3].split()) # warning: to check if tags exist, use: M2.tags
#def hasM2tags(M2): return M2[3] # warning: returns space delimited tag-string, not bool
# M2.added
# M2.modified
# M2.phash
# SETTERS:
def setM2filepath(M2,e): return M2tuple(M2[0],e,M2[2],M2[3],M2[4],M2[5],M2[6])
def setM2hash(M2,e):     return M2tuple(M2[0],M2[1],e,M2[3],M2[4],M2[5],M2[6])
def setM2tags(M2,e): # expects a set of tags
    #e = u' '.join(sorted(e)) if e else u''
    e = ' '.join(e) if e else ''
    return M2tuple(M2[0],M2[1],M2[2],e,M2[4],M2[5],M2[6])
def setM2added(M2,e):    return M2tuple(M2[0],M2[1],M2[2],M2[3],e,M2[5],M2[6])
def setM2modified(M2,e): return M2tuple(M2[0],M2[1],M2[2],M2[3],M2[4],e,M2[6])
def setM2phash(M2,e):    return M2tuple(M2[0],M2[1],M2[2],M2[3],M2[4],M2[5],e)
#def setM2meta(M2,e):    return M2#M2tuple(M2[0],M2[1],M2[2],M2[3],M2[4],M2[5],M2[6],e)
def genM2(filepath='', hash=None, tags='', added=None, modified=None, phash=None): # input UNICODE for filepath and tags!
    if hash is None and filepath and os.path.exists(filepath): # file without hash:
        hash = hashfile(filepath)
        phash = None if phash is False else imhash(filepath)
    return M2tuple(None,filepath,hash,tags,added,modified,phash)

def M2rem_tag(M2, tag):
    tags = getM2tags(M2) # set
    try: tags.remove(tag)
    except: return M2
    return setM2tags(M2,tags)
def M2add_tag(M2, tag):
    tags = getM2tags(M2) # set
    if tag in tags:
        return M2
    tags.add(tag)
    return setM2tags(M2, tags)
def M2rename_tag(M2, old_tag, new_tag):
    tags = getM2tags(M2)
    if old_tag in tags:
        tags.remove(old_tag)
        tags.add(new_tag)
        return setM2tags(M2,tags)
    return M2
#def M2debug_tags(M2): # removing empty, duplicated and sorting
#    return setM2tags(M2,getM2tags(M2))#.discard(None))
def M2file_is_missing(M2): # or hash doesn't match
    if not M2.filepath:
        return True
    elif os.path.isfile(M2.filepath) and hashfile(M2.filepath) == M2.hash:
        return False
    elif filepath_is_remote(M2.filepath):
        return False # cannot determine REMOTELY
    return True
def M2is_remote(M2, *specific_scheme):
    if not M2.filepath:
        return not specific_scheme
    if specific_scheme:
        return urlparse(M2.filepath).scheme in specific_scheme
    else:
        return urlparse(M2.filepath).scheme in remote_schemes
def M2is_idea(M2):
    return M2.filepath.startswith('idea:')

def slice_select_metadata(M2seq, slices=None):
    if not filter(None, slices): return M2seq
    selection = flatten_list([ slice_select(M2seq,sl) for sl in slices if is_slice(sl)]) if cmds else M2seq
    return MOP.filter_duplicate_metadata(selection)

def filepath_is_remote(filepath, *specific_scheme):
    if specific_scheme:
        return urlparse(filepath).scheme in specific_scheme
    else:
        return urlparse(filepath).scheme in remote_schemes
def filepath_is_idea(filepath):
    return filepath.startswith('idea:')
def filepath_is_link_as_idea(filepath):
    return filepath.startswith('idea:') and os.path.isfile(filepath[5:])

functional_tags = {
                    '^local' : lambda r: r.filepath and os.path.isfile(r.filepath),
                    '^file'  : lambda r: r.filepath and os.path.exists(r.filepath),
                    '^url'   : lambda r: r.filepath and not r.filepath.startswith('idea:') and M2is_remote(r),
                    '^idea'  : lambda r: r.filepath.startswith('idea:'),
                    '^image' : lambda r: bool(r.phash),
                    '^broken': lambda r: M2file_is_missing(r), # missing or hash mismatch
                    '^healthy':lambda r: not M2file_is_missing(r), # missing or hash mismatch
                    '^missing':lambda r: r.filepath and os.path.isfile(r.filepath) and not os.path.exists(r.filepath) # displaced, broken link
                  }
functional_tags['^text'] = functional_tags['^idea'] # alias
functional_tags['^link'] = functional_tags['^url'] # alias
functional_tags['^lost'] = functional_tags['^missing'] # alias

# DEBUGGING / PARSING TOOL:
def parse_inclusions(cmds, operator=None, substitution=True):
    include, exclude, tinclude, texclude = None, None, None, None
    inclusion = True # default action for search is inclusion
    tag = True # default action is tag search, not text search
    cmds = filter(None,cmds.strip().split())

    for cmd in cmds:
        if   cmd == '-': inclusion, tag = False, True;  continue # exclude tag
        elif cmd == '+': inclusion, tag = True,  True;  continue # include tag
        elif cmd == '_': inclusion, tag = False, False; continue # exclude text
        elif cmd == '=': inclusion, tag = True,  False; continue # include text
        elif inclusion:
            if tag:
                if not include: include = [cmd]
                else: include.append(cmd)  # include tag in search
            else:
                if not tinclude: tinclude = [cmd]
                else: tinclude.append(cmd) # include text in search
        else:
            if tag:
                if not exclude: exclude = [cmd]
                else: exclude.append(cmd)  # exclude tag in search
            else:
                if not texclude: texclude = [cmd]
                else: texclude.append(cmd) # exclude text in search
    # debug: remove duplicates
    if include:
        include = set(include)
    if exclude:
        exclude = set(exclude)
    # debug: remove interferences in buffer
    if include and exclude:
        for x in tuple(include):
            if x in exclude:
                include.remove(x)
                exclude.remove(x)

    if include:
        incspec = include.intersection(functional_tags.keys())
        if incspec:
            for tag in incspec:
                include.remove(tag)
        else:
            incspec = None
    else:
        incspec = None

    if exclude:
        excspec = exclude.intersection(functional_tags.keys())
        if excspec :
            for tag in excspec:
                exclude.remove(tag)
        else:
            excspec = None
    else:
        excspec = None

    if substitution:
        # wordnet word->tag similarity substitution:
        available_tags = set(operator.tags+operator.subtags)
        if include:
            include = change_all_similar_words_to_tags(list(include), available_tags, 0.6)
        if exclude:
            exclude = change_all_similar_words_to_tags(list(exclude), available_tags, 0.6)
    return include, exclude, tinclude, texclude, incspec, excspec

def sub_category_match(partial, whole):
    """returns True or False wether some elements in listA exist in listB in the same order"""
    index_match = 0
    for e in whole:
        if e == partial[index_match]:
            index_match += 1
            if index_match == len(partial):
                return True
    return False

class MetadataOperator(object): # nfr(object) # operations on db
    """A metadata operator. Stores db related in memory for faster responsiveness. Handles db operations for metadata."""
    #global cfg
    def __init__(self, database_path=None):
        self.db = None # stored in memory
        self.alias_db = None # stored in memory
        self.variant_db = None # stored in memory
        self.raw_db = None # stored in memory (unicode)
        self.tags = list()    # stored in memory (needs update on changes)
        self.subtags = list()
        self.aliases = list() # stored in memory (needs update on changes)
        # remembers last search:
        self.search_cmd = None#tuple()
        self.search_result = list()
        self.add_buffer = None#set()
        self.rem_buffer = None#set()
        self.mem = dict()#list()
        self.modified = False
        if database_path:
            self.set_database(database_path)
        self.motd = None # message of the day, reloaded on database set
    def reset(self):
        self.search_cmd = tuple()
        self.search_result[:] = list()
        self.add_buffer = set()
        self.rem_buffer = set()
        #self.mem[:] = list()
        self.mem.clear()
        self.modified = False
    def set_database(self, database=None, mode_index=0):
        if self.connected():
            try:
                #clrln(' [*] Closing the database...')
                if self.modified: self.db.cleanup(); self.db.close()
                if self.modified: self.alias_db.cleanup(); self.alias_db.close()
                if self.modified: self.variant_db.cleanup(); self.variant_db.close()
                if self.modified: self.raw_db.cleanup(); self.raw_db.close()
                #clrln()
            except:
                print_exception()
        if database:
            self.reset()
            self.db = TS_Base(database)
            self.alias_db = TS_Base(os.path.sep.join((database, 'buzhug_alias_db')))
            self.variant_db = TS_Base(os.path.sep.join((database, 'buzhug_variant_db')))
            self.raw_db = TS_Base(os.path.sep.join((database, 'buzhug_raw_db'))) # additional text stored here
            mode = ('open', 'override')[mode_index]
            self.db.create(('filepath',unicode), ('hash',str), ('tags',unicode),
                           ('added',datetime.datetime), ('modified',datetime.datetime), mode=mode)
            self.db.open()
            self.alias_db.create(('alias',unicode), ('selection',unicode), mode=mode)
            self.alias_db.open()
            self.variant_db.create(('variants',str), mode=mode)
            self.variant_db.open()
            self.raw_db.create(('filepath',unicode), ('hash',str), ('raw',unicode),
                           ('added',datetime.datetime), ('modified',datetime.datetime), mode=mode)
            self.raw_db.open()

            # for version compatibility:
            if not 'phash' in self.db.field_names: self.db.add_field('phash',str)
            if 'meta' in self.db.field_names: self.db.drop_field('meta')

            self.update_tags()
            self.update_aliases()
            # cwd follows database:
            os.chdir(os.path.dirname(database.rstrip('\\/' if os.name=='nt' else os.path.sep)))
        else:
            self.db, self.alias_db, self.variant_db = None, None, None # stored in memory

        # PROCESS MOTD and/or SCRIPT:
        try: filepath = os.path.join(database, 'motd.txt')
        except: return

        if os.path.isfile(filepath) and os.path.exists(filepath):
            with open(filepath.encode('utf8'),'r') as f:
                motd = list()
                for line in f.read().decode('utf8').splitlines():
                    if line.strip().startswith('script>'):
                        raw_input_buffer.extend(line[7:].split(';'))
                        continue
                    motd.append(line)
            motd = '\n'.join(motd) # list to string
            return motd

    def connected(self):
        try: return self.db.name[:]
        except: pass # return None
    def modify_metadata_list(self, M2s, cmdln, verbose=True): # modifies metadata_list * in-place *
        if M2s is None:
            M2s = self.search_result
        cmdln = debug_tag_input(cmdln)
        cmdln = ' '.join( unalias_list(cmdln.split()) if use_aliases else cmdln.split() )
        total = len(M2s)
        pprc.reset(total)
        modified = 0
        tag_operations_total = 0
        for i,M2 in enumerate(M2s):
            if verbose:
                spin(' Applying edits to '+str(total)+' items... '+pprc.inc())
            if self.buffer_command(cmdln, getM2tags(M2)):
                M2s[i], tag_operations = self.process_buffer(M2)
                if tag_operations:
                    modified += 1
                    tag_operations_total += tag_operations
        if verbose:
            clrln() # clear spinner
        if tag_operations_total:
            self.update_tags()
            self.modified = True # flag database modification
            #return M2s,(modified, tag_operations_total)
            return (modified, tag_operations_total)
        else:
            #return M2s,None
            return None
    def buffer_command(self, cmds, tags): # add/remove tags
        #cmds = filter(None, cmds.split())
        cmds = cmds.split()
        add = True # default action for tags
        for cmd in cmds:
            if   cmd == '-': add = False
            elif cmd == '+': add = True
            else:
                self.add_buffer.add(cmd) if add else self.rem_buffer.add(cmd)
        cancel_out = self.add_buffer.intersection(self.rem_buffer)
        for x in cancel_out:
            self.add_buffer.remove(x)
            self.rem_buffer.remove(x)
        # debug: remove unnecessary tags
        self.add_buffer = self.add_buffer.difference(tags) # non existing only
        self.rem_buffer = self.rem_buffer.intersection(tags) # existing only
        return bool(self.add_buffer or self.rem_buffer)
    def process_buffer(self, M2): # updates metadata with buffered tag+-, saves to db
        processed = 0

        # -- CONVENIENT TAG-EDIT PARSER: --
        old__new = list()
        def keep(tag):
            o_n = convenient_tag_edit_parser(tag, M2.tags)
            if o_n:
                old__new.extend(o_n) # add or replace
                return False
            return True
        #self.rem_buffer = set(tag for tag in self.rem_buffer if keep(tag))
        self.add_buffer = set(tag for tag in self.add_buffer if keep(tag))
        #print old__new
        for o_n in old__new:
            if o_n[0] is None: # create tag
                self.add_buffer.add(o_n[1])
            else: # modify tag
                self.rem_buffer.add(o_n[0])
                self.add_buffer.add(o_n[1])
        # -- END OF CONVENIENT TAG EDIT PARSER --

        #for unwanted_tag in M2.rem_buffer: M2.rem_tag(unwanted_tag)
        while self.rem_buffer:
            new_tag = self.rem_buffer.pop()
            if new_tag in self.aliases:
                cprint(' [!] Cannot remove "'+BRIGHT+new_tag+NORMAL+'". Such alias exists.')
            else:
                old = getM2tags(M2)
                new = M2rem_tag(M2,new_tag)
                if old != getM2tags(new):
                    M2 = new
                    processed += 1
        while self.add_buffer:
            new_tag = self.add_buffer.pop()
            if new_tag in self.aliases:
                cprint(' [!] Cannot create "'+BRIGHT+new_tag+NORMAL+'". Such alias exists.')
            else:
                old = getM2tags(M2)
                new = M2add_tag(M2,new_tag)
                if old != getM2tags(new):
                    M2 = new
                    processed += 1
        if processed:
            M2 = self.save(M2)
        return M2, processed
    def total(self):
        return str(len(self.search_result))
    def update_tags(self): # update memorised tag pool from db
        self.tags[:] = list()
        self.subtags[:] = list()
        for tags in [rec.tags.split() for rec in self.db.select() if rec.tags]:
            self.tags.extend(tags)
            self.subtags += [x for e in tags if ':' in e  for x in e.split(':') if x] # [['apple','red'],['car','fast']] -> ['apple','red','car','fast'] (non-empty)
        # debug: remove duplicates, sort for readability
        self.tags = sorted(set(self.tags))
        self.subtags = sorted(set(self.subtags))
    def update_aliases(self):
        self.aliases[:] = [rec.alias for rec in self.alias_db.select()]
        # sort for readability
        self.aliases.sort()
    def update_variants(self): # update & fix
        no_blank_delimiters = self.variant_db.select(None,'p.search(variants)',p=re.compile('^[\S]*$')) # no whitespaces, tabs etc. # http://stackoverflow.com/a/446298
        for rec in no_blank_delimiters: # = single variant in record
            self.variant_db.delete(rec)
            self.modified = True # flag database modification
    def search(self, include=None, exclude=None, tinclude=None, texclude=None, incspec=None, excspec=None, verbose=False, in_selection=False, sort=True, cmd=None, ret_only=False):
        #print ('+',include, '-',exclude, '=',tinclude, '_',texclude, '^+',incspec, '^-',excspec)
        time_started = datetime.datetime.now()
        self.search_cmd = cmd
        if not in_selection and None == include == exclude == tinclude == texclude == incspec == excspec:
            search_result = self.db
        else:
            if in_selection:
                records = tuple( e.rec for e in self.search_result )
            else:
                records = self.db
            if tinclude: tinclude = tuple( e.lower() for e in tinclude )
            if texclude: texclude = tuple( e.lower() for e in texclude )
            search_result = [ spin(suffix=' Searching...', embed=record) for record in records
                if  (include  is None or all( # all inclusions in a record match
                                            any(sub_category_match(i.split(':'), tag.split(':'))
                                            for tag in filter(None,record.tags.split()+[record.hash])) for i in include
                                            )
                    )
                and (tinclude is None or all(i in (record.tags+' '+record.filepath).lower() for i in tinclude))
                if  (exclude  is None or all(
                                            not any(sub_category_match(i.split(':'), tag.split(':'))
                                            for tag in filter(None,record.tags.split()+[record.hash])) for i in exclude
                                            )
                    )
                and (texclude is None or all(i not in (record.tags+' '+record.filepath).lower() for i in texclude))]
            clrln()
        if not ret_only:
            del self.search_result[:]#self.search_result[:] = list()

        # lastly (narrower selection) filter result by special, functional tags if any given:
        if incspec:
            for tag in incspec:
                #search_result = filter(functional_tags[tag], search_result)
                search_result = [ r for r in search_result if functional_tags[tag](r) ]
        if excspec:
            for tag in excspec:
                #search_result = itertools.ifilterfalse(functional_tags[tag], search_result)
                search_result = [ r for r in search_result if not functional_tags[tag](r) ]

        if not search_result and verbose:
            cprint(' [!] No matches.')
        else:
            if full_path_in_title:
                set_console_title('* '+self.db.name+'{?}'+nfr_title)
            else:
                set_console_title(os.path.basename('* '+self.db.name)+'{?}'+nfr_title)
            if verbose and not buffer_mode: cprint(' [*] Search result:\n')
            pprc.reset(len(search_result))
            new_search_result = list()
            search_result_append = new_search_result.append # <- for performance
            for i,rec in enumerate(search_result):
                spin(' Loading metadata... '+pprc.inc())
                try:
                    M2 = rec2M2(rec) # M2
                except KeyboardInterrupt:
                    if really(' Cancel?', default=True):
                        if sort:
                            M2_sort_nicely(new_search_result)
                            if not ret_only:
                                #print 'FILTERING1'
                                self.search_result = new_search_result
                        return new_search_result
                #===========================
                search_result_append(M2)
                #===========================
                if verbose and not buffer_mode:
                    clrln()
                    self.show_info(M2, str(i+1))
            clrln()
            if verbose and not buffer_mode: print ''
        if sort:
            M2_sort_nicely(new_search_result)
        #if err and not buffer_mode and (datetime.datetime.now()-time_started).total_seconds() > 3.0:
        if not buffer_mode and (datetime.datetime.now()-time_started).total_seconds() > 3.0:
            cprint(' [i] Indexed in '+str((datetime.datetime.now()-time_started).total_seconds())+' seconds.')
        if not ret_only:
            #print 'FILTERING2'
            self.search_result = new_search_result
        return new_search_result
    def match_in_db(self, M2=None,hash=None,filepath=None, multiple=False): # searches for matching hash (hash or filepath must be provided or returns None)
        if M2 and M2.rec:
                return M2.rec
        if M2 and M2.hash: # hash
                match = self.db.select(hash=str(M2.hash))
        elif M2 and M2.filepath: # filepath
                match = self.db.select(filepath=unicode(M2.filepath))
        elif hash:
            match = self.db.select(hash=str(hash))
        elif filepath:
            match = self.db.select(filepath=unicode(filepath))
        else:
            return None
        if multiple:
            return match if match else None # returns matching records, a list of records
        else:
            return match[0] if match else None # returns the 1st record, not the list of records
    def save(self, M2, index=None): # NOW RETURNS SAVED ITEM (UPDATED!)
        """ Updates database, and optionally MOP.search_result if index given. Returns saved M2 """
        self.modified = True # flag database modification
        d = datetime.datetime.now()
        if not M2.rec: # insert into db
            dbi = self.db.insert(filepath=unicode(M2.filepath), hash=M2.hash,
                    tags=u' '.join(sorted(getM2tags(M2))), added=d, modified=d, phash=M2.phash)
            M2 = rec2M2(self.db[dbi]) # update metadata with record
        else: # update db record
            M2.rec.update(filepath=unicode(M2.filepath), tags=u' '.join(sorted(getM2tags(M2))), added=M2.added, modified=d, phash=M2.phash)
        M2 = setM2modified(M2,d)
        if not index is None:
            self.search_result[index] = M2
        return M2
    def remove(self, M2, index=None):
        if M2.rec:
            if M2.hash:
                self.remove_variant_by_hash(M2.hash) # remove from variants
            self.db.delete(M2.rec) # remove from database
            if not index is None:
                del self.search_result[index]
            self.modified = True # flag database modification
            return True
        return False
    def update(self, M2=None, hash=False, phash=False, create=True): # from hash, OR just fill in default values (for new instances)
        if M2 and M2.rec:
            match = M2.rec
        elif hash:
            match = self.match_in_db(hash=hash)
        else:#if not match:
            match = self.match_in_db(M2) # from hash or filepath

        if match: # update instance info. no changes for: hash
            M2 = rec2M2(match)
        elif create: # update instance with default values
            d = datetime.datetime.now()
            # metadata = (record=0 filepath=1 hash=2 tags=3 added=4 modified=5 phash=6)
            M2 = M2tuple(M2.rec,M2.filepath,M2.hash,'',d,d,None)
        else:
            return None # <- M2 is not in the database
        return M2
    def show_info(self, M2, title=None, filepath=True, hash=True, hashes=False, tags=True, modified=True, short=True):
        global consoleX
        present = True
        if title:
            title = title[:consoleX]
            cprint( TINT+'_'+BRIGHT+title+NORMAL+'_ ' *((consoleX-2 - len(title))/2)+DULL )
        M2filepath = M2.filepath
        is_idea = filepath_is_idea(M2filepath)
        if is_idea:
            M2filepath = M2filepath[5:]
        if filepath:
            #with open(M2filepath,'rb') as f:
            #    print len(f.read())/1024, 'KB'
            if M2filepath:
                if filepath_is_remote(M2filepath):
                    if is_idea and filepath_is_idea(M2filepath):
                        cprint( TINT+'IDEA: '+BERRORT+'&&'+TINT+M2filepath.replace('idea:','')+DULL )
                    elif is_idea:
                        cprint( TINT+'REMOTE: '+BLIME+'&^'+TINT+M2filepath+DULL )
                    else:
                        cprint( TINT+'REMOTE: '+BLIME+'^'+BDULL+M2filepath+DULL )
                elif os.path.isfile(M2filepath):
                    filepath=os.path.basename(M2filepath) if short else M2filepath
                    if is_idea:
                        cprint( TINT+'FILE: '+BLIME+'&^'+TINT+filepath+DULL )
                    else:
                        cprint( TINT+'FILE: '+BDULL+filepath+DULL )
                    if WTlib:
                        mime = WTlib.identify_file(M2filepath)[0]
                        if mime:
                            cprint( TINT+'MIME/TYPE: '+DULL+mime )
                else:
                    if is_idea:
                        cprint( ansi_definition(tint('IDEA: '), M2filepath, width=consoleX-2), markup=True )
                    else:
                        cprint( ERRORT+'LOST: '+BRIGHT+M2filepath+DULL )
                        present = False
            else:
                if is_idea:
                    cprint( ERRORT+'GENERIC: '+BRIGHT+'nameless idea'+DULL )
                else:
                    cprint( ERRORT+'GENERIC: '+BRIGHT+'nameless item'+DULL )
        if hash and M2.hash:
            if present:
                check = hashfile(M2filepath) if M2filepath and os.path.isfile(M2filepath) else '(can\'t verify hash - file is missing)'

            if not is_valid_default_hash(M2.hash):
                cprint( TINT+'HASH: '+BRIGHT+'nonstandard'+DULL+' '+M2.hash )

            elif present and M2.hash == check:
                cprint( tint('HASH: ')+M2.hash+' '+tint(default_algo.__name__.replace('openssl_','')) )
                if hashes and M2filepath and os.path.isfile(M2filepath):
                    cprint(  '      '+hashfile(M2filepath, md5)+tint(' md5') )

            else:
                cprint( tint('HASH: ')+M2.hash+' '+tint(default_algo.__name__.replace('openssl_','')) )
                if present:
                    cprint(  '      '+BERRORT+str(check)+NORMAL+' (now)'+DULL )
                    if hashes and M2filepath and os.path.isfile(M2filepath):
                        cprint( '      '+hashfile(M2filepath, md5)+tint(' md5 (now)') )

            if M2.phash:
                cprint( '      '+M2.phash+tint(' pHash') )

            if present and hashes:
                #print 'DATAINFO:', datainfo(M2.filepath)
                data = datainfo(M2.filepath)
                if data and data['type'] == 'image':
                    cprint(tint('IMAGE-SPECIFIC:')+'\n size: '+str(data['dimensions'][0])+' x '+str(data['dimensions'][1])+'\n format: '+data['format']+'\n mode: '+data['mode'])
                    if data.has_key('description'): cprint(' description: '+data['description'])
        if tags:
            if M2.tags:
                cprint( ansi_definition(tint('TAGS: '), tint_special_chars(' '.join(slash_join_tags(sorted(getM2tags(M2))))),width=consoleX-2) )
            else:
                cprint(ERRORT+'TAGLESS'+DULL)
        if M2.hash:
            variants = MOP.hash_variants_by_hash(M2.hash)
            if variants:
                cprint( tint('VARIANTS: ')+str(variants.count(' ')+1) )#+' files' )
        if modified:
            if M2.added is None:
                cprint( tint('MODIFIED: ')+'not saved' )
            else:
        #        cprint( tint('MODIFIED: ')+str(M2.modified)+', '+humanize_date_difference(datetime.datetime.now(), M2.modified, offset=None) )
                #print str(M2.modified)#print humanize_date_difference(datetime.datetime.now(), M2.modified)
                #maya_now = maya.now()
                #cprint( tint('MODIFIED: ')+str(M2.modified))#+', '+str(humanize_date_difference(datetime.datetime.now(), M2.modified)) )
                cprint( TINT+'ADDED: '+DULL+maya.parse(str(M2.added)).slang_time()+TINT+' MODIFIED: '+DULL+maya.parse(str(M2.modified)).slang_time())#+', '+str(humanize_date_difference(datetime.datetime.now(), M2.modified)) )
    def add_variant_by_hash(self, hash1, hash2):
        if hash1 == hash2:
            return 0
        # select_for_update
        recs1 = self.variant_db.select(None,'p.search(variants)',p=re.compile(hash1)) # in the list
        recs2 = self.variant_db.select(None,'p.search(variants)',p=re.compile(hash2)) # in the list
        new_group = list()#set()
        if recs1:
            for rec in recs1:
                new_group.extend(rec.variants.split())
            self.variant_db.delete(recs1)
            self.modified = True # flag database modification
        else:
            new_group.append(hash1)
        if recs2:
            for rec in recs2:
                new_group.extend(rec.variants.split())
            self.variant_db.delete(recs2)
            self.modified = True # flag database modification
        else:
            new_group.append(hash2)
        uniqueTruthy(new_group)
        self.variant_db.insert(variants=str(' '.join(new_group)))
        self.modified = True # flag database modification
        return len(new_group)
    def remove_variant_by_hash(self, hash): # remove hash from the variants
        hash = str(hash)
        recs = self.variant_db.select(None,'p.search(variants)',p=re.compile(hash)) # in the list
        recs = [ rec for rec in recs if hash in rec.variants.split() ] # no partial hash matches
        if recs:
            new_variants = recs[0].variants.split()
            #cprint(' [i] Removing hash: '+hash)
            new_variants.remove(hash)
            if len(new_variants) > 1: # variants of 1 not allowed
                recs[0].update(variants=str(' '.join(new_variants)))
            else: # remove record
                self.variant_db.delete(recs[0])
                self.modified = True # flag database modification
    def get_metadata_variants_by_hash(self, hash): # returns metadata elements existing in the same variants
        hash = str(hash)
        recs = self.variant_db.select(None,'p.search(variants)',p=re.compile(hash)) # in the list
        #recs = [ rec for rec in recs if hash in rec.variants.split() ] # no partial hash matches
        if recs:
            metadata_variants = list()
            hashes = recs[0].variants.split()
            for h in hashes:
                M2 = self.update(hash=h) # create/update M from hash
                metadata_variants.append(M2)
            return metadata_variants
        else:
            return None
    def hash_variants_by_hash(self, hash): # returns None or space-delimited hashes (including parent hash)
        if not hash: return None
        recs = self.variant_db.select(None,'p.search(variants)',p=re.compile(hash)) # in the list
        if recs:
            return recs[0].variants
        else:
            return None
    def filter_duplicate_metadata(self, M2s=None):
        if M2s is None:
            M2s = self.search_result[:]
        for i,M2 in enumerate(M2s):
            if M2.hash:
                if M2.hash in map(lambda x:x.hash if x else None, M2s[:i]):
                    M2s[i]=None
            elif M2.filepath in map(lambda x:x.filepath if x else None, M2s[:i]):
                M2s[i]=None
        return filter(None,M2s)

    #def FIX_hash_clones(self, M2s=None, prompt=False): # warning: won't check for file existence
    #    scope = [M2.rec for M2 in M2s if M2.hash] if M2s else self.db.select(hash!=str(''))
    #    hash_clones = dict()
    #    for rec in scope:
    #        if rec.hash not in hash_clones.keys():
    #            hash_clones[rec.hash] = set(rec)
    #            continue
    #        hash_clones[rec.hash].add(rec)
    #    for hash in hash_clones.keys():
    #        while len(hash_clones[hash])>1:
    #            # check for data match:
    #            for clone in hash_clones[hash][1:]:
    #                comparison = hash_clones[hash][0]
    #                if clone.tags == comparison.tags and clone.phash == comparison.phash:
    #                    pass#merge
    #                    self.merge_metadata(clone, comparison)
    #                elif

    def fix_empty(self): # removes nameless and hashless items
        empty = [ rec for rec in self.db if not rec.filepath and not rec.hash ]
        if empty:
            self.modified = True # flag database modification
            self.db.delete(empty)
            self.update_tags()
            cprint(' [i] Removed '+str(len(empty))+' nameless and hashless items.')
    def fix_variants(self):
        self.modified = True # flag database modification
        empty = [ rec for rec in self.variant_db if not rec.variants or ' ' not in rec.variants ]
        if empty:
            self.variant_db.delete(empty)
            self.modified = True # flag database modification
        known_hashes = set(rec.hash for rec in self.db if rec.hash)
        change = False
        if known_hashes:
            for rec in self.variant_db:
                hash_group = set(rec.variants.split())
                hashes = [ hash for hash in hash_group if hash in known_hashes ] # retain only hashes of files present in the db
                if len(hashes) < 2:
                    self.variant_db.delete(rec)
                    change=True
                elif len(hashes) != len(hash_group) or set(hashes) != hash_group:
                    rec.update(variants=str(' '.join(hashes)))
                    change=True
            if change:
                self.update_variants()
                self.modified = True # flag database modification
    def fix_slashes(self): # rewrites slash-joined tags in the db with separated tags
        self.modified = True # flag database modification
        slashed = tuple( rec for rec in self.db if rec.tags and ('/' in rec.tags or '\\' in rec.tags) )
        for rec in slashed:
            #if rec.phash:
            #    rec.update(phash=str(rec.phash))
            t = rec.tags.split()
            for i,tag in enumerate(t):
                t[i] = ' '.join(slash_split_tag(tag))
            t = ' '.join(t)
            t = ' '.join(sorted(set(t.split())))
            rec.update(tags=unicode(t))
        self.update_tags()
    def rec_match_merge_duplicates(self, match):
        self.modified = True # flag database modification
        tags_merged = ' '.join( rec.tags for rec in match )
        tags_merged = ' '.join(sorted_unique(tags_merged.split()))
        match[0].update(tags=unicode(tags_merged))
        self.db.delete(match[1:])
    def fix_duplicates(self): # removes duplicate hash matches and joins tags
        self.modified = True # flag database modification
        global consoleX
        removed = 0
        local = tuple( rec for rec in self.db if rec.hash )
        total = pprc.reset(len(local))
        for rec in local:
            spin(' Fixing file duplicates... '+pprc.inc())
            match = tuple( m for m in local if m.hash==rec.hash )
            if len(match) > 1:
                self.rec_match_merge_duplicates(match)
                clrln()
                cprint(' [!] Removed '+str(len(match)-1)+' duplicate(s): '+str(match[0].hash))
                removed += 1
        clrln()
        cprint(' [i] '+str(removed)+' unique(s).\n [i] Fixing idea duplicates...') if removed else clrln(' [i] Fixing idea duplicates...')
        removed = 0
        remote = [ rec for rec in self.db if not rec.hash ]
        ideas = [ rec for rec in remote if rec.filepath and rec.filepath.startswith('idea:') ] # hack
        for rec in ideas:
            match = [ m for m in local if os.path.normcase(m.filepath)==os.path.normcase(rec.filepath) ]
            if len(match) > 1:
                self.rec_match_merge_duplicates(match)
                if not removed: print ''
                cprint(' [!] Removed '+str(len(match)-1)+' duplicate idea(s):\n '+str(match[0].filepath[5:consoleX+3]))
                removed += 1
        clrln()
        cprint(' [i] '+str(removed)+' unique(s).\n [i] Fixing remote url duplicates...') if removed else clrln(' [i] Fixing remote url duplicates...')
        removed = 0
        remote_url = [ rec for rec in remote if rec.filepath and not rec.filepath.startswith('idea:') ] # hack
        for rec in remote_url:
            match = [ m for m in local if os.path.normcase(m.filepath)==os.path.normcase(rec.filepath) ]
            if len(match) > 1:
                self.rec_match_merge_duplicates(match)
                if not removed: print ''
                cprint(' [!] Removed '+str(len(match)-1)+' duplicate remote url(s):\n '+str(match[0].filepath))
                removed += 1
        if removed: cprint(' [i] '+str(removed)+' unique(s).')
    def fix_db(self):
        self.modified = True # flag database modification
        sourceless = tuple( rec for rec in self.db if not rec.hash and not rec.filepath )
        for rec in sourceless:
            self.db.delete(rec)
            cprint(' [!] Removing sourceless entry.')
        self.update_tags()
    def rehash(self, select_hashed=True, select_skipped=True): # rehashes selected files
        self.modified = True # flag database modification
        rec_selection = [ M2.rec for M2 in self.search_result ]
        skipped = 0
        total = pprc.reset(len(rec_selection))
        time_started = datetime.datetime.now()
        for i,rec in enumerate(rec_selection):
            clrln()
            spin(' Re-hashing... '+pprc.inc())
            if not filepath_is_remote(rec.filepath) and os.path.isfile(rec.filepath) and os.path.exists(rec.filepath):
                new_hash = hashfile(rec.filepath)
                if rec.hash and new_hash != rec.hash:
                    clrln(' '+str(rec.hash)+' -> '+str(new_hash)+'\n')
                if 1 or not rec.phash or new_hash != rec.hash:
                    new_phash = imhash(rec.filepath)
                    if new_phash != rec.phash:
                        print btint(' <o>'),
                        rec.update(phash=str(new_phash))
                        spin(' Re-hashing... '+pprc.inc(0))
                        print tint(' <o>'),
                if new_hash != rec.hash:
                    rec.update(hash=str(new_hash))
            else:
                skipped += 1
                if rec.hash:
                    clrln('\n '+ERRORT+rec.hash+' -> Error: displaced or not a file\n '+rec.filepath+DULL+'\n\n')
                elif rec.filepath:
                    if rec.filepath.startswith('idea:'):
                        clrln(' '+ERRORT+(rec.filepath[5:default_algo_length]).rjust(default_algo_length)+' -> Error: idea\n'+DULL)
                    elif filepath_is_remote(rec.filepath):
                        clrln(' '+ERRORT+rec.filepath[:default_algo_length]+' -> Error: remote url?\n'+DULL)
                        if len(rec.filepath) > default_algo_length: clrln(' '+ERRORT+rec.filepath+DULL+'\n')
                    else:
                        clrln('\n '+ERRORT+(os.path.basename(rec.filepath)[-default_algo_length:]).rjust(default_algo_length)+' -> Error: displaced file?\n '+rec.filepath+DULL+'\n\n')
                        if len(rec.filepath) > default_algo_length: clrln(' '+ERRORT+rec.filepath+DULL+'\n')
                else:
                    clrln(' '+ERRORT+('?'*default_algo_length)+' -> Error: displaced or not a file\n'+DULL)

        if not buffer_mode and (datetime.datetime.now()-time_started).total_seconds() > 60.0:
            clrln()
            cprint(' [i] Hashed in '+str((datetime.datetime.now()-time_started).total_seconds())+' seconds.')

        clrln(' [i] Updating, please wait... ')
        hashed__metadata = [ (True,self.update(rec2M2(rec))) if rec.hash and not filepath_is_remote(rec.filepath) and os.path.isfile(rec.filepath) else (False,rec2M2(rec)) for rec in rec_selection ]
        self.search_result = [ hM2[1] for hM2 in hashed__metadata if hM2[0] and select_hashed or not hM2[0] and select_skipped ]
        clrln()
        if skipped:
            cprint(' [i] '+BRIGHT+str(total-skipped)+NORMAL+' updated. '+BRIGHT+str(skipped)+NORMAL+' skipped.')
        elif total==1:
            cprint(' [i] Updated.')
        else:
            cprint(' [i] All Updated.')
    def get_intersecting_tags(self, M2s=None):
        if M2s is None:
            M2s = self.search_result
        setList = ( getM2tags(M2) for M2 in M2s )
        return sorted(list(set.intersection(*setList)))
    def get_unique_tags(self, M2s=None):
        if M2s is None:
            M2s = self.search_result
        # all the intersections combined and uniquified
        intersecting = set()
        all = getM2tags(M2s[0])
        for i,M2 in enumerate(M2s[1:]):
            all.update(getM2tags(M2))#all.extend(M.tags)
            shared = set.intersection(getM2tags(M2s[i-1]),getM2tags(M2))
            if shared:
                intersecting.update(shared)
        # all - intersecting
        return sorted(all - intersecting)
    def get_rare_tags(self, M2s=None): # <------------ NOT WORKING
        # rare = occurring in less than all metadata objects
        if M2s is None:
            M2s = self.search_result
        setList = ( getM2tags(M2) for M2 in M2s )
        #all = sum(setList)
        all = set.union(*setList)
        return sorted(rare)
    def memLoad(self, k):
        return self.mem[k] if self.mem.has_key(k) else None
    def memSave(self, k, v):
        self.mem[k] = v
    def merge_metadata(self, M1, M2, tags=True, group=True, modify_db=True, new_filepath=True):
        """ Replaces hashables (on modify_db) or creates a new merged (tags, groups) metadata based on M1. """
        merged_tags = list()
        #print M1, M2
        if M1.tags: merged_tags.extend(getM2tags(M1))
        if M2.tags: merged_tags.extend(getM2tags(M2))
        #print '\nmerg:',M1.tags,M2.tags
        if modify_db:
            modify_db = M1.hash and M2.hash # must have hashes
            if not modify_db: cprint(' [!] Can\'t modify - hashless item.')
        merged_tags = ' '.join(sorted(set(merged_tags))) if tags else M1.tags
        if group and M2.hash:
            match1 = self.variant_db.select(None,'p.search(variants)',p=re.compile(M1.hash))
            match2 = self.variant_db.select(None,'p.search(variants)',p=re.compile(M2.hash))
            variants1 = match1[0].variants if match1 else ''
            variants2 = match2[0].variants if match2 else ''
            merged_variants = ' '.join((variants1,variants2))
            if modify_db:
                self.modified = True # flag database modification
                self.variant_db.delete(match1+match2)
                #self.variant_db.delete(match2)
                self.variant_db.insert(variants=str(merged_variants))
                self.remove_variant_by_hash(M2.hash) # non-existent

        filepath = M2.filepath if new_filepath else M1.filepath

        M3 = M2tuple(None, filepath, M1.hash, merged_tags, M1.added, datetime.datetime.now(), M1.phash)

        if modify_db:
            self.modified = True # flag database modification
            #print ''
            #print M3
            match1 = self.db.select(hash=str(M1.hash))
            match2 = self.db.select(hash=str(M2.hash))
            self.db.delete(match2)
            self.db.delete(match1)
            M3 = self.save(M3)
            #print '\nSave1:',M3
        return M3
    def msg_on_tag(self, rule):
        raw, msg = rule[0], rule[1]
        search_result = None
        # 1. EXPAND ALIASES IF ANY:
        if set(self.aliases).intersection(raw.split()): # alias detected
            #alias_detected = True
            cmds = filter(None,raw.strip().split())
            for i,cmd in enumerate(cmds):
                if cmd in self.aliases:
                    match = self.alias_db.select(alias=unicode(cmd))
                    if match:
                        cmds[i] = match[0].selection
                        if ' | ' in cmds[i]:
                            cmds[i] = ' | ' + cmds[i] + ' | ' # miessing-up raw with "|" (ORs)
            raw = ' '.join(cmds)
            if ' | ' in raw: # cleaning-up the "|" (ORs) overkill in raw
                raw = ' | '.join(filter(None,raw.split(' | ')))
        # 2. DO BULK TAG-SEARCH:
        if ' | ' in raw: # "if" because aliases don't have to contain _ORs
            if ' * ' in raw:
                _AND = ' '.join(raw.split(' * ')[1:]) # debug for multiple asterisks
                raw = raw.split(' * ')[0]
            else:
                _AND = ''
            _ORs = filter(None,raw.split(' | '))
            _ORs = map(lambda x:x.strip(),_ORs)
            selections = list()
            for i,_OR in enumerate(_ORs):
                _ORs[i] = _OR = ' '.join((_OR, _AND))
                inc,exc,tin,tex,sinc,sexc = parse_inclusions(_OR, self, use_wordnet)
                operations = flatten_list(filter(None,[inc,exc,tin,tex,sinc,sexc]))
                if not any(operations):
                    #if skippy and not buffer_mode:
                    #    cprint(' [i] Search aborted.')
                    continue
                selections.append(Selection(inc,exc,tin,tex,sinc,sexc))
            raw = ' | '.join(_ORs)
            #if not cmd_ln_mode or not buffer_mode:
            #    print ' [i] Request: '+raw
            #buffer_mode = True
            search_result = BulkOperation(selections).run(self, verbose=False, over_selection=True, ret_only=True)
            #if addMode: search_result = search_result+previous_search
            search_result = self.filter_duplicate_metadata()
        # 3. OR ORDINARY TAG-SEARCH:
        else:
            inc,exc,tin,tex,sinc,sexc = parse_inclusions(debug_tag_input(raw), self, use_wordnet)
            operations = flatten_list(filter(None,[inc,exc,tin,tex,sinc,sexc]))
            if not any(operations):
                return None
            else:
                #buffer_mode = True # won't disply index timing
                search_result = Selection(inc,exc,tin,tex,sinc,sexc).select(self, verbose=False, from_selection=True, ret_only=True)#self.search(raw)
                #if addMode: search_result = self.filter_duplicate_metadata(search_result+previous_search)
        #print '2', raw, msg
        if search_result:
            #print '3', raw, msg
            cprint(msg.replace('%n%',str(len(search_result))))
            return search_result
        else:
            return None

def convenient_tag_edit_parser(tag_op, tag_pool):
    """
    convenient_tag_edit_parser(string, list) -> list of tuple: [(old, new), ...]
    Ex: tag+1 -> tag:1
        tag+1 -> tag:2
    """
    oprs = '+-'
    operator_present = tuple(tag_op.count(opr) for opr in oprs)
    if sum(operator_present) == 1:
        opr = oprs[operator_present.index(True)]
        tag,val = part(tag_op,opr)
        if is_number(val):
            if tag+':' in tag_pool:
                old__new = list()
                for t in tag_pool.split():
                    if t.startswith(tag+':'):
                        s,rest = part(t[len(tag)+1:],':')
                        if is_number(s):
                            s = str(int(s).__add__(int(opr+val))) # add or subtract
                            old = t
                            if rest:
                                old__new.append( (old,tag+':'+s+':'+rest) )
                            else:
                                old__new.append( (old,tag+':'+s) )
                if old__new:
                    return old__new # replacement or new
                else:
                    return [(None, tag+':'+str(int(opr+val)))]
            else:
                return [(None, tag+':'+str(int(opr+val)))]
    return None

from nfr_text import *

def remove_duplicate_files(dir_with_unwanted_ext, undo=True):
    if len(dir_with_unwanted_ext) == 1:
        dir, skip_files_ending_with = dir_with_unwanted_ext[0], None
    else:
        dir, skip_files_ending_with = dir_with_unwanted_ext[0], dir_with_unwanted_ext[1].split()
    if os.path.exists(dir):
        if skip_files_ending_with:
            fh = [(os.path.join(dirpath, f), None if f.endswith(skip_files_ending_with)
                                                  else hashfile(os.path.join(dirpath, f)))
                  for dirpath, dirnames, files in os.walk(dir)
                  for f in files]# if f.endswith('')]
        else:
            fh = [(os.path.join(dirpath, f), hashfile(os.path.join(dirpath, f)))
                  for dirpath, dirnames, files in os.walk(dir)
                  for f in files]# if f.endswith('')]
        fh.sort(key=lambda x: os.path.getctime(x[0]), reverse=False)
        preserved = 0
        unique_hashes = list()
        total = len(fh)
        for i,(f,h) in enumerate(fh):
            spin(' Removing duplicates... '+str(percent(i,total))+'%')
            if h is None:
                try: send2trash(f)
                except: print_exception()
            elif h not in unique_hashes:
                unique_hashes.append(h)
                preserved += 1
            else:
                if undo:
                    try: send2trash(f)
                    except: print_exception()
                else:
                    try: os.remove(f)
                    except: print_exception()
        clrln()
        return preserved, total
    else:
        return 0, 0

# "SELECTIONS":
# DEBUGGING / PARSING TOOLS:
def inclusions_to_cmd(include=None, exclude=None, tinclude=None, texclude=None, incspec=None, excspec=None):
    #print ('+',include, '-',exclude, '=',tinclude, '_',texclude, '^+',incspec, '^-',excspec)
    if not any((include, exclude, tinclude, texclude, incspec, excspec)):
        return ''
    cmd = tuple()
    if include:
        cmd += tuple(include)
    if incspec:
        cmd += tuple(incspec)
    if exclude:
        cmd += ('-',)+tuple(exclude)
    if excspec:
        cmd += tuple(excspec)
    if tinclude:
        cmd += ('=',)+tuple(tinclude)
    if texclude:
        cmd += ('_',)+tuple(texclude)
    return ' '.join(cmd)

class BulkOperation(object):
    def __init__(self, selections=list()):
        self.selections = selections
        self.cmds = ()
    def run(self, operator, verbose=False, over_selection=False, ret_only=False): # updates: result, cmds
        result, self.cmds = list(), tuple()
        for selection in self.selections:
            result.extend(selection.select(operator, verbose, from_selection=over_selection, ret_only=ret_only))
            self.cmds = self.cmds + (selection.cmd,)
        result = sorted(operator.filter_duplicate_metadata(result)) # no duplicates, sort
        operator.search_cmd = tuple(' | '.join(self.cmds))
        operator.search_result = result
        return result

class Selection(object): # selection definition with optional get/select mechanism
    def __init__(self, inc=None, exc=None, tin=None, tex=None, sinc=None, sexc=None):
        # sets or None
        self.include  = inc#[:] if inc else None
        self.exclude  = exc#[:] if exc else None
        self.tinclude = tin#[:] if tin else None
        self.texclude = tex#[:] if tex else None
        self.incspec  = sinc
        self.excspec  = sexc
        #print ('+',inc, '-',exc, '=',tin, '_',tex, '^+',sinc, '^-',sexc)
        self.cmd = inclusions_to_cmd(inc, exc, tin, tex, sinc, sexc) # <-- values are not modified
    def select(self, operator, verbose=False, from_selection=False, sort=True, ret_only=False): # updates: include and exclude
        return operator.search(self.include, self.exclude, self.tinclude, self.texclude, self.incspec, self.excspec, verbose, from_selection, sort=sort, cmd=self.cmd, ret_only=ret_only)

def secure_file_copy(src, dst, file_operation=shutil.copy2):
    if os.path.isfile(dst):
        if hashfile(src) == hashfile(dst): return dst
        filename, ext = os.path.splitext(ntpath.basename(src))
        dst_root = ntpath.dirname(dst)
        i = 0
        while 1:
            dst = os.path.join(dst_root, filename+' ('+str(i)+')'+ext)
            if not os.path.isfile(dst): break
            i += 1
    file_operation(src, dst)
    return dst

#-------------------------------------------------------------------------------
#
# COMPLEX FUNCTIONS
#
#-------------------------------------------------------------------------------

import urllib # remote file download
def add_single_item(raw=None, verbose=True, idea=False, hash=False):
    #global addMode, custom_download_directory
    """
    Creates metadata item, saves or updates it from database. Returns True if it was selected.
    """
    if raw is None:
        readline.set_completer(complete.path)
        raw = rawc_input(' Item to add/modify: [skip] ').strip()
        if part1(raw) in kw.addByHash:
            hash = True
            raw = part2(raw)

    while raw:
        if not idea and not filepath_is_remote(raw) and not hash:
            raw = format_path(raw) # WINDOWS
        file_downloaded = None
        if filepath_is_remote(raw, 'http','https') and (auto_download_extensions and os.path.splitext(raw)[1].lower() in auto_download_extensions or (not buffer_mode and really(' Try downloading remote file?'))) and not hash:
            remote_file = urllib.URLopener()
            #dl_path = os.path.join(custom_download_directory, os.path.basename(MOP.db.name)) # every database has it's subdir
            dl_path = custom_download_directory[:] # every database has it's subdir
            dst = os.path.join(dl_path,ntpath.basename(urlparse(raw).path))
            if not os.path.exists(dl_path):
                try:
                    os.makedirs(dl_path)
                except:
                    print_exception()
                    return False # = file was NOT selected
            try:
                clrln(' [i] Downloading...')
                remote_file.retrieve(raw, dst)
                clrln()
                cprint(' [+] Saved as: '+BRIGHT+dst+NORMAL)
                #cprint(' [+]         : '+BRIGHT+custom_download_directory+NORMAL)
                file_downloaded = dst[:]
                raw = dst # pass the filepath on as raw input (path formatted already)
            except:
                cprint(' [-] Download failed:\n '+BRIGHT+raw+NORMAL)
                return False # = file was NOT selected

        if os.path.isfile(raw) or filepath_is_remote(raw) or hash:
            if hash:
                M2 = genM2(filepath=None, hash=str(raw)) # create metadata from hash
            else:
                M2 = genM2(filepath=raw) # create metadata from filepath (filepath & hash)
            if auto_copy_hash and M2.hash:
                xerox.copy(str(M2.hash))
                if verbose:
                    cprint(' [i] Hash copied to clipboard.')
            db_match = MOP.match_in_db(M2)
            if db_match: # DUPLICATE METADATA!
                M2 = MOP.update(M2) # updates metadata from db record (from filepath or hash)
                #M2 = rec2M2(db_match) # slightly faster than M = MOP.update(M)
                if verbose:
                    if not is_samepath(raw, M2.filepath): # filepath don't match, hash matches only
                        #print (raw, M2.filepath)
                        #print (os.path.realpath(raw) == os.path.realpath(M2.filepath))
                        #cprint('\n [i] This file is already present but locations differ:')
                        cprint('\n [!] Identified (duplicate) as:')
                given_filepath = M2.filepath
                if M2file_is_missing(M2):
                    if verbose:
                        print ''; MOP.show_info(M2, hash=False); print ''
                    if not verbose or really(' You\'ve found a missing file! Save new filepath to database?', default=True, n=' [*] Skipping\n'):
                        #M2 = setM2filepath(M2, given_filepath)
                        M2 = setM2filepath(M2, raw)
                        M2 = MOP.save(M2)
                    if verbose:
                        if M2.phash:
                            cprint(' [*] Saved (pHashed'+(')' if M2.tags else ', tagless)'))
                        else:
                            cprint(' [*] Saved'+('' if M2.tags else ' (tagless)'))
                elif verbose:
                    print ''; MOP.show_info(M2, hash=False, short=False); print ''
                if file_downloaded:
                    try: send2trash(file_downloaded)
                    except: print_exception()
                MOP.search_result = [M2]
                if tag_msg:
                    for rule in tag_msg:
                        msg_on_tag_matches = MOP.msg_on_tag(rule)
                return True # = file was selected
            else: # NEW METADATA!, INSERT
                # updates metadata with timestamp
                d = datetime.datetime.now()
                M2 = setM2added(M2,d)
                M2 = setM2modified(M2,d)
                M2 = setM2phash(M2,imhash(raw))
                M2 = MOP.save(M2) # saves metadata to database
                if verbose:
                    if M2.phash:
                        cprint(' [*] Saved (pHashed, tagless)')
                    else:
                        cprint(' [*] Saved (tagless)')
                if addMode:
                    MOP.search_result.append(M2)
                    #MOP.search_result = MOP.filter_duplicate_metadata(MOP.search_result) # same objects but different adresses!!
                    MOP.filter_duplicate_metadata(MOP.search_result) # same adresses
                else:
                    MOP.search_result = [M2]
                return True # = file was selected
        elif not raw:
            return False # = file was NOT selected
        else:
            cprint(' [!] Invalid idea/link or non-existent file specified: '+raw)
            return False # = file was NOT selected
    return False # = file was NOT selected (no raw input)

def unalias(alias):
    global use_aliases
    if not use_aliases: return alias
    match = MOP.alias_db.select(alias=unicode(alias))
    if match:
        return match[0].selection
    return expandvars_nfr_only(alias)
def unalias_query(q):
    qs = q.split()
    while set(qs).intersection(set(MOP.aliases)):
        for i,e in enumerate(qs):
            if e in MOP.aliases:
                e = unalias(e)
                if ' | ' in e:
                    qs[i] = '( '+e+' )'
                else:
                    qs[i] = e
    return ' '.join(qs)

#def get_input_default(match):
#    return match.group(1)
def unalias_list(cmds, resolve_input=True):
    rewrite = True
    while rewrite:
        rewrite = False
        for i,cmd in enumerate(cmds):
        #i = -1
        #while cmd in cmds:
            #i += 1
            if resolve_input and re.search(r'\{.*?\}',cmd):#'{input}' in cmd:
                #print str(len(cmds))+' > '+str(i+1)
                if len(cmds) > i+1:
                    #cmds[i] = cmd.replace('{input}',' '.join(cmds[i+1:]))
                    #cmds[i] = re.sub(r'\{(.*?\)}',get_input_default,cmd)
                    cmds[i] = re.sub(r'\{.*?\}',' '.join(cmds[i+1:]),cmd)
                    cmds = cmds[:i+1]
                else:
                    #cmds[i] = cmd.replace('{input}','')
                    #cmds[i] = re.sub(r'\{(.*?)\}',get_input_default,cmd)
                    cmds[i] = re.sub(r'\{(.*?)\}',lambda x: x.group(1),cmd)
                break
            if ':' in cmd:
                subcmds = cmd.split(':')
                subcmds = map(unalias, subcmds)
                rewritten = ':'.join(subcmds)
                if cmds[i] != rewritten:
                    cmds[i] = rewritten
                    #print 'A'
                    rewrite = True
            else:
                rewritten = unalias(cmd)
                if cmds[i] != rewritten:
                    cmds[i] = rewritten
                    #print 'B'
                    rewrite = True
        #if rewrite:
        #    print cmds
    return cmds

def space2underscore(match):
    return match.group(1).replace(' ','_')
def backticks2underscore(s):
    while s.count('`') >= 2:
        s = re.sub(r'`([^\ ].*?)`', space2underscore, s)
    return s
def space2underscore_quotation(match):
    return '"' + match.group(1).replace(' ','_') + '"'
def double_backtick2underscore(s):
    while s.count('``') > 1:
        s = re.sub(r'``([^\ ].*?)``', space2underscore_quotation, s)
    if s.count('``') == 1:
        if '```' in s:
            s = s.replace('```','``')
        s = s.partition('``')
        s = s[0] + '"' + s[2].replace(' ','_') + '"'
    return s

def is_valid_tag(tag):
    return tag not in (' ', '\t', None) + _ALL_KW_ + reserved
def is_valid_default_hash(word):
    if len(word) != default_algo_length:
        return False
    for c in word:
        if not c in '0123456789abcdef':
            return False
    return True

from iniparse import INIConfig # https://code.google.com/p/iniparse/
def config_file_has_all_options_defined(filepath):
    try:
        cfg = INIConfig(open(filepath))
        options = (
                   cfg.default.full_path_in_title,
                   cfg.default.database_path,
                   cfg.default.database_locations,
                   cfg.default.startup_command,
                   cfg.default.use_wordnet,
                   cfg.default.custom_temporary_directory,
                   cfg.default.tint,
                   cfg.default.browser_command,
                   cfg.default.platform,
                   cfg.default.auto_download_extensions,
                   cfg.default.custom_download_directory,
                   cfg.default.auto_copy_hash,
                   cfg.default.exit_commands,
                   cfg.default.extra_folder_tag
                   #cfg.default.technical_info # default = False on exception
                  )
        for test in options:
            test.strip()
    except:
        return False
    return True
def save_config_file(filepath, config):
    with open(filepath,'w') as f: f.write(config)
def change_config(config, key, value):
    ret = list()
    for line in config.split(os.linesep):
        if line.startswith(key+' ') or line.startswith(key+'='):
            if value is None:
                ret.append(key + ' = ')
            else:
                ret.append(key + ' = ' + str(value))
        else:
            ret.append(line)
    return os.linesep.join(ret)

def friendly_relative_path(path):
    if path.find('.'+os.path.sep)==0:
        return path[2:]
    return path

#-------------------------------------------------------------------------------
#
# MAIN
#
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    set_console_title(nfr_title)

    config_filepath = os.path.join(SCRIPT_DIR,'nfr.ini')
    first_run = not os.path.isfile(config_filepath)

    #---------------------------------------------------------------------------
    # USING CONFIGURATION FILE:
    clrln(' [*] Loading configuration file...')
    if not os.path.isfile(config_filepath) or not config_file_has_all_options_defined(config_filepath):
        # CROSS-PLATFORM SETTINGS ##############################################
        config = ('[default]\n\n'

                  '# Full database path displayed in console window (may not work in some cases):\n'
                  'full_path_in_title = False\n\n'

                  '# Initial database or directory (determines the working directory at startup):\n'
                  #'database_path = '+os.path.join('db','default')+'\n\n'
                  #'database_path = \n\n'
                  'database_path = db\n\n'

                  '# Where to search (recursively) for databases:\n'
                  'database_locations = .\n\n'

                  '# Optional command(s) to run at startup:\n'
                  'startup_command = \n\n'

                  '# If use_wordnet is set to True, remember to run "-wordnet-download" command, as well.\n'
                  'use_wordnet = \n\n'

                  'custom_temporary_directory = ~temp\n\n'

                  '# Tints are: red, green, yellow, blue, magenta, cyan, white\n'
                  'tint = cyan\n\n'

                  '# Enter multiple file extensions using space as separator:\n'
                  'auto_download_extensions = \n\n'

                  '# %nfr% location will be used as root dir if path is relative:\n'
                  'custom_download_directory = downloads\n\n'

                  '# Auto-copy file\'s hash value on input?\n'
                  'auto_copy_hash = False\n\n'

                  '# Specify an exit command if <enter> is too tricky:\n'
                  'exit_commands = \n\n'

                  '# Files having this special tag, will be grouped in an extra folder after a move/copy operation.\n'
                  'extra_folder_tag = @\n\n'

                  '# Automations for recursive directory selection:\n'
                  'enable_folder_autotagging = True\n'
                  '# A file-path containing this indicator will auto-tag all contents using folder names:\n'
                  'folder_autotagging_indicator = @tagged\n'
                  '# A file-path containing this indicator will auto-group all contents:\n'
                  'folder_autogrouping_indicator = @group\n\n'

                  '# Display additional info used for debugging:\n'
                  'technical_info = False\n\n'

                  '# Display message on matching tag(s) in selection (decreases performance a bit):\n'
                  '#tag_msg = tag1 tag2 | tag3 -msg: [!] Example message on selection tag-match.; tag1 -msg: [i] Another tag match info.\n'
                  'tag_msg = \n\n'

                  '# File extension to automagically run as script:\n'
                  'auto_script_extension = .nfr\n\n'

                  '# Crude, default browser command to display files (using custom_temporary_directory as fringe):\n'
                 )
        # WINDOWS SETTINGS #####################################################
        if os.name == 'nt': # https://stackoverflow.com/questions/1325581/how-do-i-check-if-im-running-on-windows-in-python
            config += ('browser_command = C:\\Program Files\\IrfanView\\i_view32.exe|/thumbs\n\n' if os.path.isfile('C:\Program Files\IrfanView\i_view32.exe') else 'browser_command = explorer.exe\n\n')
            config += ('# Cross-platform header constant. Do not modify.\nplatform = nt\n\n')
        else:
            # NOT-WINDOWS SETTINGS #############################################
            known_apps = (('gthumb',),('eog',),('geeqie',)) # mirage, ristretto
            app_found = False
            for app in known_apps:
                if which(app[0]):
                    app_found = True
                    config += 'browser_command = '+'|'.join(app)+'\n\n'
                    break
            if not app_found:
                print ''
                cprint(' [!] Please, set a file-browsing app in the config file ('+config_filepath+').')
                config += 'browser_command =\n\n'
            config += ('# Cross-platform header constant. Do not modify.\nplatform = unix\n\n')
        save_config_file(config_filepath, config)

    cfg = INIConfig(open(config_filepath))
    cfg_platform = cfg.default.platform.strip()
    nt2unix = os.name != 'nt' and cfg_platform == 'nt'
    full_path_in_title = yN(cfg.default.full_path_in_title)

    database_path = path_nt2unix(cfg.default.database_path.strip()) if nt2unix else cfg.default.database_path.strip()
    if not database_path:
        #database_path = os.path.join('db', 'default')
        database_path = None
    else:
        if not os.path.isabs(database_path):
            database_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),database_path)
        #if not os.path.exists(os.path.dirname(database_path)):
        if not os.path.exists(database_path):
            #os.makedirs(os.path.dirname(database_path))
            os.makedirs(database_path)
        os.chdir(os.path.dirname(database_path)) # because database-follow is default at MOP init
        if not path_is_buzhug_db(database_path): # in case database_path is not a database, use it as a current working directory:
            os.chdir(database_path)
            database_path = None
    if cfg.default.database_locations.strip():
        if nt2unix:
            database_locations = list(set( path_nt2unix(path.strip()) for path in cfg.default.database_locations.split(';') if path.strip() ))
        else:
            database_locations = list(set( path.strip() for path in cfg.default.database_locations.split(';') if path.strip() ))
        database_locations = filter_subdirs(database_locations)
    determined_database_locations = None

    startup_command = cfg.default.startup_command
    if not startup_command:
        startup_command = None
    use_wordnet = yN(cfg.default.use_wordnet)
    temporary_directory = path_nt2unix(cfg.default.custom_temporary_directory.strip()) if nt2unix else cfg.default.custom_temporary_directory.strip()
    if not temporary_directory:
        temporary_directory = '~temp'
    if not os.path.isabs(temporary_directory):
        temporary_directory = os.path.join(SCRIPT_DIR,temporary_directory)
    # colors:
    determine_color = cfg.default.tint.strip().lower()
    if ' ' in determine_color:
        determine_color = part1(determine_color)
    colors = {
                '0 red'       :Fore.RED,
                #'1 lred'      :Fore.LIGHTRED_EX,
                '1 green'     :Fore.GREEN,
                #'3 lgreen'    :Fore.LIGHTGREEN_EX,
                '2 yellow'    :Fore.YELLOW,
                #'5 lyellow'   :Fore.LIGHTYELLOW_EX,
                '3 blue'      :Fore.BLUE,
                #'7 lblue'     :Fore.LIGHTBLUE_EX,
                '4 magenta'   :Fore.MAGENTA,
                #'9 lmagenta'  :Fore.LIGHTMAGENTA_EX,
                '5 cyan'      :Fore.CYAN,
                #'11 lcyan'    :Fore.LIGHTCYAN_EX,
                '6 white'     :Fore.WHITE
                #'13 lwhite'   :Fore.LIGHTWHITE_EX,
                #'14 black lblack'    :Fore.LIGHTBLACK_EX
             }
    color_labels = sorted(flatten_list(e.split() for e in colors.keys()))
    def get_color(s): # returns label's color-code or None
        try: s = s.split[0]
        except: pass
        for k,v in colors.iteritems():
            if s in k.split():
                return v
    #back_color_codes = (Back.BLACK, Back.RED, Back.GREEN, Back.YELLOW, Back.BLUE, Back.MAGENTA, Back.CYAN, Back.WHITE)
    determine_color = get_color(determine_color)
    if determine_color:
        TINT = determine_color

    system_cmd_for_directory_preview = map(str.strip,filter(None,cfg.default.browser_command.split('|')))
    auto_download_extensions = filter(None,cfg.default.auto_download_extensions.strip().lower().replace('.','').split())
    auto_download_extensions = tuple('.'+ext for ext in auto_download_extensions)
    custom_download_directory = path_nt2unix(cfg.default.custom_download_directory.strip()) if nt2unix else cfg.default.custom_download_directory.strip()
    if not custom_download_directory:
        custom_download_directory = 'downloads'
    #if not os.path.isabs(custom_download_directory):
    #    custom_download_directory = os.path.join(SCRIPT_DIR,custom_download_directory)
    auto_copy_hash = yN(cfg.default.auto_copy_hash)
    exit_commands = filter(None,cfg.default.exit_commands.strip().split())
    extra_folder_tag = cfg.default.extra_folder_tag.strip().replace('"','').replace('/',':').replace('\\',':')
    while extra_folder_tag.startswith('-'):
        extra_folder_tag = extra_folder_tag[1:]
    if not extra_folder_tag:
        extra_folder_tag = '@'

    enable_folder_autotagging = yN(cfg.default.enable_folder_autotagging)
    folder_autotagging_indicator = cfg.default.folder_autotagging_indicator.strip()
    folder_autogrouping_indicator = cfg.default.folder_autogrouping_indicator.strip() # variant/version grouping

    try:
        tag_msg = filter(None,cfg.default.tag_msg.split(';'))
        for i,rule in enumerate(tag_msg):
            try:
                rule = rule.split('-msg:')
                tag_msg[i] = (rule[0].strip(), rule[1])
            except:
                tag_msg[i] = None
        tag_msg = filter(None,tag_msg)
    except:
        tag_msg = None

    try:
        TECHNICAL_INFO = yN(cfg.default.technical_info)
    except:
        TECHNICAL_INFO = False
    auto_script_extension = cfg.default.auto_script_extension.strip()
    clrln()
    #----------------------------------------------------------------------------

    import nfr_help as help
    kw = help.kw
    kw.exit += ' ' + ' '.join(exit_commands)
    kw.make() # conversion from space delimited string to tuple

    if first_run:
        cprint(center_text(BRIGHT+__nfr__.capitalize()+' '+__version__+NORMAL))
        print center_text(__website__)
        if os.name == 'nt':
            cprint('# Please remember to backup your files.\n# Try `-cfg` for settings, `-h` for help or `-<tab>` for commands.', markup=True)
        else:
            cprint('# Please remember to backup your files.\n# Try `-cfg` for settings, `-h` for help or `-<tab><tab>` for commands.', markup=True)
        cprint( TINT+('_ '*(consoleX/2))+DULL )

    # QUICK WORDNET-USE SWITCHES:
    if len(sys.argv) > 1:
        for i,arg in enumerate(sys.argv[1:]):
            if arg in kw.wordnetOff:#('-w-','-wordnet-'):
                use_wordnet = False
                sys.argv.remove(arg)
                break
    if len(sys.argv) > 1:
        for i,arg in enumerate(sys.argv[1:]):
            if arg in kw.wordnetOn:#('-w+','-wordnet+','-w','-wordnet'):
                use_wordnet = True
                sys.argv.remove(arg)
                break
    arguments = len(sys.argv) > 1
    wordnet_init = False
    if use_wordnet:
        wordnet_init = True
        # https://stackoverflow.com/questions/18871706/check-if-two-words-are-related-to-each-other
        clrln(' [*] Loading Wordnet...')
        from nltk.corpus import wordnet as wn
        clrln()
        from itertools import product
        def similar_word_from_list(word, word_list, minscore=0.6):
            if not word_list:
                return word, 0
            sem1 = wn.synsets(word)
            total = pprc.reset(len(word_list))
            for i,w in enumerate(word_list):
                spin(' Replacing "'+BRIGHT+word+NORMAL+'"... '+pprc.inc())
                sem2 = wn.synsets(w)
                maxscore = 0
                for s1,s2 in list(product(*[sem1,sem2])):
                    score = s1.wup_similarity(s2) # Wu-Palmer Similarity
                    # #score = s1.lch_similarity(s2)
                    # #score = s1.res_similarity(s2)
                    #score = s1.jcn_similarity(s2)
                    #score = s1.lin_similarity(s2)
                    maxscore = score if maxscore < score else maxscore
                word_list[i] = (maxscore, w)
                word_list.sort()
            clrln()
            #print word_list[:-10]
            score, similar_word = word_list[-1]
            #print str(score)+' '+similar_word
            if score >= minscore:
                return similar_word, score
            else:
                return word, 0
        def change_all_similar_words_to_tags(words, tags, tolerance=0.6, verbose=True):
            for i,word in enumerate(words):
                if word in tags:
                    continue # next word
                if ':' in word and any(sub_category_match(word.split(':'),tag.split(':')) for tag in tags if ':' in tag):
                    continue # next word
                if not is_valid_default_hash(word):
                    if verbose: cprint(' [i] Replacing "'+BRIGHT+word+NORMAL+'"...', newline=False)
                    similar,score = similar_word_from_list(word, list(tags), tolerance)
                    if similar != word:
                        words[i] = similar
                        if verbose:
                            clrln()
                            cprint(' [i] Changed: "'+BRIGHT+word+NORMAL+'" to "'+BRIGHT+similar+NORMAL+'" ('+str(int(round(score,2)*100))+'%)')
                    elif verbose:
                        clrln()
                        cprint(' [!] No match for "'+BRIGHT+word+NORMAL+'" was found.', newline=False)
                        if len(words) == 1 or really(' Skip this tag?', default=False):
                            words[i] = None
                elif verbose:
                    cprint(' [i] Integrating '+BRIGHT+'hash'+NORMAL+' search.')
                    if i > 0:
                        words[i] = ' | '+word
            words = filter(None, words)
            return words

    clrln(' [*] Loading objects...')

    MOP = MetadataOperator(database_path)
    #DBA_NAME = MOP.db.name
    #SELECTION = Selection()
    #try: os.remove(errlog_filepath)
    #except: pass

    #looper = Looper('_'*(consoleX/10))
    spinner_animation = tuple(BERRORT+c+DULL for c in '-\\|/')
    spinner = Looper(spinner_animation)
    spin = spinner.animate

    additional_completions = list()
    specific_selection = False
    total = 0 # selected

    _CONFIG_KW_ = kw.cpl('db cfg cls exit wordnetDl wordnetOn wordnetOff wordnetInfo website chdir aliasOff clipb2img')+kw.cpl('defMode defModeNew addMode addModeNew subMode subModeNew about motd delay')
    _GLOBAL_KW_ = kw.cpl('refresh heal')
    _HELP_KW_ = kw.help
    _SUBSELECTION_KW_ = (
        ' '.join(     kw.cpl('fix lost detach remove t'))
        +' '+' '.join(kw.cpl('copy copyFollow move RMDF RMDFx'))
        +' '+' '.join(kw.cpl('alias aliasRemove idea'))
        +' '+' '.join(kw.cpl('rename renameMatchingGroup renameMatchingWhole list listMore listMore2 listLess dir'))
        +' '+' '.join(kw.cpl('present edit over less equal'))
        +' '+' '.join(kw.cpl('group ungroup variants variantsAdd variantsSub'))
        +' '+' '.join(kw.cpl('inverse c open browse count rawCopy'))
        +' '+' '.join(kw.cpl('local remote links ideas ct ctSplit makeFilelist makeCollage x color'))
        +' '+' '.join(kw.cpl('rehash ch cm'))
        +' '+' '.join(kw.cpl('intersection difference rare'))
        +' '+' '.join(kw.cpl('similar pSimilar similarFuz pSimilarFuz memSave memLoad memList script export sort reverse shuffle'))
        +' '+' '.join(kw.cpl('runClipboard iterClipboard'))
    ).split()
    _TAG_SELECTION_KW_ = ' '.join(kw.cpl('subselect')).split()
    reserved = tuple(('-x x -with with  + -   ;').split())
    forbidden_dirs = ('\\ / . .. a: b: c: d: e: f: g: h: i: j: k: l: m: n: o: p: r: s: t: u: v: w: x: y: z: a:/ b:/ c:/ d:/ e:/ f:/ g:/ h:/ i:/ j:/ k:/ l:/ m:/ n:/ o:/ p:/ r:/ s:/ t:/ u:/ v:/ w:/ x:/ y:/ z:/').split()

    _ALL_KW_ = filter(None,
        _CONFIG_KW_ +
        _GLOBAL_KW_ +
        _HELP_KW_   +
        tuple(_SUBSELECTION_KW_) +
        tuple(_TAG_SELECTION_KW_))

    _ALL_KW_ = list(_ALL_KW_)
    for word in kw.p:
        if word in _ALL_KW_:
            _ALL_KW_.remove(word)
    _ALL_KW_ = tuple(_ALL_KW_)

    raw_input_buffer = list()

    addMode = None

    clrln() # wipes "Loading..." indicator

    def promptMode():
        if addMode is None:
            return '> '
        return BRIGHT+'+ '+NORMAL if addMode is True else BRIGHT+'- '+NORMAL

    slice_mem = 0 # remembers last slice from -* command

    while 1:
        sourceless_hash = False
        raw = None
        if addMode:
            previous_search = MOP.search_result[:]
        #formatting-------------------------------------------------------------
        consoleX, consoleY = get_terminal_size() # update between commands
        clrln() # clears line

        buffer_mode = False
        cmd_ln_mode = True
        #formatting-------------------------------------------------------------
        if raw_input_buffer:
            #clrln(' [i] Script lines left to execute: '+BRIGHT+str(len(raw_input_buffer))+NORMAL)
            #spin()
            buffer_mode = True
            raw = raw_input_buffer.pop(0).strip()
            #if not raw_input_buffer: clrln()

        #formatting-------------------------------------------------------------
        # USER INPUT
        elif startup_command or arguments:
            if arguments:
                raw = ' '.join(sys.argv[1:]).decode('utf-8').strip()#.decode(sys.stdin.encoding).strip()
            if startup_command:
                if arguments:
                    raw = ';'.join((startup_command, raw))
                else:
                    raw = startup_command
                startup_command = None
            arguments = False
        elif MOP.connected():
            complete.set_custom(sorted(set(
            MOP.tags + MOP.subtags + MOP.aliases + list(_ALL_KW_) + additional_completions + functional_tags.keys()
                                )))
            readline.set_completer(complete.custom)
            readline.set_completer_delims(' \\/;')

            if specific_selection or len(MOP.search_result)==1:
                try:
                    M2filepath = MOP.search_result[0].filepath
                    selection_id = M2filepath[5:] if filepath_is_idea(M2filepath) else M2filepath[:]

                    if M2filepath in (None,''):
                        selection_id = error_btint('generic\\nameless')
                    else:
                        # TRIMMING AND ADDING "..."
                        if os.path.isfile(M2filepath.replace('idea:','')):
                            selection_id = os.path.basename(M2filepath)
                            if len(selection_id) > consoleX/2:
                                name,ext = os.path.splitext(selection_id)
                                selection_id = name[:-2-(len(selection_id)-consoleX/2)] + '..' + ext
                        elif len(selection_id) > consoleX/2:
                            selection_id = selection_id[:(consoleX/2)-3]+'...'
                        if filepath_is_remote(M2filepath):
                            if filepath_is_idea(M2filepath):
                                if os.path.isfile(M2filepath[5:]):
                                    selection_id = BLIME+'&^'+TINT+selection_id+DULL
                                else:
                                    selection_id = BLIME+'&'+TINT+selection_id+DULL
                            else:
                                selection_id = BLIME+'^'+TINT+selection_id+DULL
                        elif M2file_is_missing(MOP.search_result[0]):
                            selection_id = error_btint(selection_id)
                        else:
                            selection_id = btint(selection_id)
                    if not MOP.search_result[0].tags: # tagless
                        selection_id = ERRORT+'#'+DULL+selection_id
                except:
                    cprint(' [!] Search returned no results.')
                    selection_id = ''
                prompt = tint(ntpath.basename(MOP.db.name))+'{'+selection_id+'}'+promptMode()
            else:
                prompt = tint(ntpath.basename(MOP.db.name))+'{'+btint(str(len(MOP.search_result)))+'}'+promptMode()
            cmd_ln_mode = False
            if full_path_in_title:
                set_console_title(MOP.db.name+'{'+str(len(MOP.search_result))+'}'+nfr_title)
            else:
                set_console_title(os.path.basename(MOP.db.name)+'{'+str(len(MOP.search_result))+'}'+nfr_title)
            while 1:
                raw = rawc_input(prompt).strip()
                if not raw.startswith('-i ') and not raw.startswith('-idea ') and not raw.startswith('idea:') and '-*' in raw and complete.options:
                    raw = part2(raw,'-*')
                    if not raw and len(complete.options) > slice_mem+1:
                        raw = str(slice_mem+1)
                    if is_slice(raw):
                        if not ':' in raw:
                            slice_mem = int(raw)
                        raw = ' '.join(slice_select(complete.options, raw))
                        if raw:
                            if part1(raw) in _ALL_KW_:
                                cprint(' [!] Please enter commands manually.')
                                continue
                            cprint(prompt+raw)
                            xerox.copy(str(raw))
                            break
                        cprint(' [!] Index out of range [1..'+str(len(complete.options))+'].')
                        continue
                    cprint(' [!] Expected slice input for index [1..'+str(len(complete.options))+'].')
                else:
                    break
            #if complete.options: print complete.options, 'chosen'
        else: # no MOP.db
            cprint(BRIGHT+TINT+'\n [i] Please open or create a database.\n'+DULL)
            cprint(help.get('-db')[:-1]+' (works as console parameter too).\n',markup=True)
            cprint(help.get('-cfg')[:-1]+' (edit default database setting and restart).\n',markup=True)
            cmds = kw.cpl('db cls exit wordnetInfo wordnetDl wordnetOn wordnetOff about website chdir color cfg help') + ('',)
            if determined_database_locations:
                cmds += determined_database_locations
            complete.set_custom(cmds)
            readline.set_completer(complete.custom)
            readline.set_completer_delims(' ')
            while raw is None or ';' in raw or not part1(raw).lower() in cmds:
                if raw:
                    if raw.strip() in _ALL_KW_:
                        cprint(' [!] Please open or create a database first.')
                    else:
                        cprint(' [!] Come again?')
                prompt = ' '+promptMode()
                raw = rawc_input(prompt).strip()
                if determined_database_locations and raw in determined_database_locations:
                    raw = '-d '+raw
                    cprint(' [!] Please use the proper command next time.')
        #formatting-------------------------------------------------------------
        x = format_path(raw)
        if auto_script_extension and os.path.splitext(x)[1]==auto_script_extension and os.path.isfile(x) and os.path.exists(x):
            raw = kw.script[0]+' '+raw
        if part1(raw) in kw.script:
            old_cwd = os.getcwd()
            script_lines_buffered = 0
            script_paths = part2(raw).split(';')
            #if not script_paths and auto_script_extension:
            #    script_paths = [ M.filepath for M in MOP.search_result if os.path.splitext(M.filepath)[1]==auto_script_extension and os.path.exists(M.filepath) ]
            for scriptpath in script_paths:
                #print 'sp1:',scriptpath
                scriptpath = os.path.realpath(format_path(scriptpath)) # absolute path
                #print 'sp2:',scriptpath
                os.chdir(os.path.dirname(scriptpath)) # change working-directopry to script-file path
                #print('AT:', os.path.dirname(scriptpath))
                with open(scriptpath, 'r') as myfile:
                    lines = myfile.readlines()
                    total = pprc.reset(len(lines))
                    for i,line in enumerate(lines):
                        spin(' Buffering script file... '+pprc.inc())
                        if not line.lstrip().startswith(';'):
                            script_lines_buffered += 1
                            raw_input_buffer.append(line)

                    clrln()
                    #if script_lines_buffered and not buffer_mode:
                    #    cprint(' [*] Loaded '+BRIGHT+str(script_lines_buffered)+NORMAL+' line(s) of script.')
            raw_input_buffer.append(kw.chdir[0]+' '+old_cwd) # revert ot old working-dir after running all script lines
            continue
        #formatting-------------------------------------------------------------
        if set(kw.aliasOff).intersection(raw.lower().split()):
            # REMOVE KW.ALIASOFF AND SET USE_ALIASES (OFF)
            raw = raw.split()
            for i,e in enumerate(raw):
                if e in kw.aliasOff:
                    raw_string = True if e == '-raw' else False
                    del raw[i]
                    break
            raw = ' '.join(raw)
            use_aliases = False
            if not raw.strip():
                cprint(' [i] Use this flag in conjunction with any command to ignore aliases.')
                continue
        else:
            use_aliases = True
            raw_string = False
        #formatting-------------------------------------------------------------
        if not raw_string:
            if not os.path.exists(format_path(raw)): # its not a path
                raw = double_backtick2underscore(raw)
                raw = backticks2underscore(raw)
        #formatting-------------------------------------------------------------
        if ' ' in raw and part1(raw) in ('*','**'): # DIRTY HACK
            raw = ';'.join(part(raw))
        #formatting-------------------------------------------------------------
        # USE ALIASES AS COMMANDS:
        if part1(raw) in kw.rawCopy:
            cmd = part1(raw)
            raw = ' '.join( unalias_list(part2(raw).split()) if use_aliases else part2(raw).split() )
            if raw:
                xerox.copy(str(raw))
                cprint(' [*] Copied.')
            else:
                cprint(' [!] Nothing to copy.')
            continue
        #formatting-------------------------------------------------------------
        raw_fallback = raw[:]
        #0----------------------------------------------------------------------
        if MOP.connected() and use_aliases and not part1(raw) in kw.cpl('idea aliasRemove') and not raw.startswith('idea:'):
            raw = ' '.join(unalias_list(raw.split(' ')) if use_aliases else raw.split(' ')) # do not alter ideas with aliases
        #-----------------------------------------------------------------------
        if not raw and exit_commands: continue # prevent exit on blank input if exit commands were defined
        #0----------------------------------------------------------------------
        if not raw or raw in kw.exit or raw in exit_commands: break
        elif ';;' in raw and use_aliases:
            raw_input_buffer = filter(None,raw.split(';;')) + raw_input_buffer
            continue # loop to get new raw input from buffer
        elif ';' in raw and use_aliases and not part1(raw) in kw.cpl('alias aliasRemove idea'):
            raw_input_buffer = filter(None,raw.split(';')) + raw_input_buffer
            continue # loop to get new raw input from buffer
        #0----------------------------------------------------------------------
        if part1(raw) in kw.delay:
            d = part2(raw)
            if d:
                if int(d) > 0:
                    sleep(int(d))
                else:
                    getch()
            continue
        #0----------------------------------------------------------------------
        if part1(raw).lower() in kw.help:
            if len(raw.split()) > 1 and part2(raw) in help.keywords:
                word = part2(raw)#.lower()
                paras = list()
                for para in help.help:
                    if not isinstance(para, str) and word in para[0].split():
                        #cprint(para[1].strip('\n'), markup=True)
                        if word in kw.cpl():
                            paras.append((para[1],' '.join(kw.aliases(word))))
                        else:
                            paras.append((para[1],None))
                # trim heading blankspaces to remove padding where no header is displayed ("---" creates a header in pseudo-markup)
                trimPadding = False if any(map(lambda para:para[0].strip().startswith('---'),paras)) else True
                padding = None
                for para in paras:
                    for ln in para[0].split('\n'):
                        if ln.strip():
                            pads = 0
                            for c in ln:
                                if c!=' ':
                                    break
                                else:
                                    pads += 1
                            if padding is None or pads < padding:
                                padding = pads
                for para in paras: # tuple( text,alias_text )
                    if trimPadding and padding:
                        cprint(' '+'\n '.join(map(lambda x:x[padding:],para[0].split('\n'))), markup=True)
                    else:
                        cprint(para[0], markup=True)
                    if para[1]:
                        cprint(ansi_definition(tint(' ALIASES: '),para[1]+'\n'))
                continue
            elif len(raw.split()) > 1 and not part2(raw) in help.keywords and not really(' Unknown keyword. Display whole help instead?'):
                continue
            cprint('\n'+center_text(btint(__about__)), markup=True)
            cprint(help.text, markup=True)
            cprint(ansi_definition(tint(' HELP ALIASES: '),' '.join(kw.help)+'\n'))
            show_expandvars_nfr_only()
            print ''
            continue
        #0----------------------------------------------------------------------
        if raw.lower() in kw.website:
            run_with_default_app(__website__)
            continue
        #0----------------------------------------------------------------------
        if part1(raw).lower() in kw.chdir:
            newDir = format_path(part2(raw))
            if newDir:
                try:
                    if os.path.isdir(newDir):
                        os.chdir(newDir)
                        #cprint(' [i] Changed directory to:\n '+newDir)
                    else:
                        cprint(' [!] Can\'t change to non-existent directory.')
                        cprint(newDir)
                except:
                    print_exception()
            else:
                cprint(' [i] That command changes the current working directory:', markup=True)
                cprint(' '+BRIGHT+os.getcwd()+NORMAL)
            continue
        #0----------------------------------------------------------------------
        if part1(raw) in kw.idea: # format
            idea = part2(raw)
            if not idea: # search for ideas in selection
                if MOP.search_result:
                    MOP.search_result = [ M2 for M2 in MOP.search_result if M2is_remote(M2,'idea') ]
                    total = len(MOP.search_result)
                else:
                    cprint(' [!] Please select some items to filter ideas from.')
                continue
            # modify input and proceed
            raw = 'idea:'+idea
            raw_fallback = raw[:]
        else:
            idea = False
        #0----------------------------------------------------------------------
        # ADD/MODIFY SINGLE FILE METADATA
        if MOP.connected() and addMode is None and (idea or not part1(raw) in _ALL_KW_ and (os.path.isfile(format_path(raw)) or filepath_is_remote(format_path(raw))) or (part1(raw) in kw.addByHash and part2(raw))):
            if part1(raw) in kw.addByHash:
                specific_selection = add_single_item(part2(raw), hash=True, verbose=not buffer_mode)
            elif idea or filepath_is_remote(format_path(raw), 'idea'):
                specific_selection = add_single_item(raw, idea=True, verbose=not buffer_mode)
            elif filepath_is_remote(format_path(raw)):
                specific_selection = add_single_item(raw, verbose=not buffer_mode)
            else:
                specific_selection = add_single_item(format_path(raw), verbose=not buffer_mode)
            total = 1
            continue
        else:
            specific_selection = False
        #0----------------------------------------------------------------------
        #npath = os.path.normpath(raw).strip('"').strip("'") # WINDOWS
        if MOP.connected() and not part1(raw) in _ALL_KW_ and os.path.isdir(format_path(part1(raw,' -m '))) and os.path.exists(format_path(raw)) and not format_path(raw) in (MOP.tags+MOP.subtags):
            # COMMAND IS A DIRECTORY, NOT A FILE/TAG:
            if ' -m ' in raw: # match substring pattern
                raw, substring = raw.partition(' -m ')[0].strip(), raw.partition(' -m ')[2].strip()
            else:
                substring = ''
            path = format_path(raw.strip()) # WINDOWS
            if path.lower() in forbidden_dirs:
                if not really(' Really select files from that directory?'): continue
            filepath_list = [ spin(suffix=' Searching directory tree...', embed=(dirpath, f))
                for dirpath, dirnames, files in os.walk(path)
                for f in files if substring in f ]
            clrln()
            collected = len(filepath_list)
            if collected>100 and not really(' Recursively add '+btint(str(collected))+' files from that directory?'):
                if skippy:
                    cprint(' [*] Skipping')
                continue
            filepaths = map(lambda x: os.path.join(*x), filepath_list)
            metadata_list = list()
            for i,filepath in enumerate(filepaths):
                metadata_list.append(genM2(filepath))
                #spin(suffix=' Figuring checksums. Please wait... '+(metadata_list[-1].hash+' ' if metadata_list[-1].hash else '')+str(i)+'/'+str(len(filepaths)))
                spin(suffix=' Figuring checksums. Please wait... '+str(i)+'/'+str(len(filepaths)))
            clrln()

            new_metadata = list()
            old_metadata = list()
            total = pprc.reset(len(metadata_list))
            folder_groups = dict()
            folder_autotagged = False
            aTagged = folder_autotagging_indicator # too informative
            aGroup = folder_autogrouping_indicator # too informative
            for i,M2 in enumerate(metadata_list):
                try:
                    # error on file move, record reference is cloned and lost? (does not reference to original?)
                    # single items are handled fine. compare both to find the bug (lines: 2290 & 1403)
                    if folder_autotagged:
                        spin(' Collecting metadata (auto-tagging)... '+pprc.inc())
                    else:
                        spin(' Collecting metadata... '+pprc.inc())

                    folder_structure = [ f for f in os.path.splitdrive(os.path.dirname(M2.filepath))[1].split(os.sep) if f ]

                    if enable_folder_autotagging and any(aTagged in f.lower().split() for f in folder_structure): # folder autotagging
                        # BUILD folder_groups, folder_tags
                        folder_autotagged = True
                        for i2,folder in enumerate(folder_structure): # truncate to leftmost `aTagged` keyword
                            if aTagged in folder.lower().split():
                                folder_structure = folder_structure[i2:]
                                break
                        group_label = None
                        for i2,folder in enumerate(folder_structure): # use URL from start to leftmost `aGroup` as group-label
                            if not group_label and aGroup in folder.lower().split():
                                group_label = os.path.join(*folder_structure[:i2+1])
                                break

                        #debugged_tag_input = debug_tag_input(' '.join(folder_structure), folder_autotagging=True)
                        debugged_tag_input = ' '.join( debug_tag_input(tag_input, folder_autotagging=True) for tag_input in folder_structure )
                        #print '\nDEBUGGED:', debugged_tag_input
                        if use_aliases: debugged_tag_input = ' '.join(unalias_list(debugged_tag_input.split()))
                        flagged = flags2dict(debugged_tag_input, (aGroup,aTagged), default=aTagged)
                        folder_tags = set(flagged[aTagged]) if flagged else None
                        #print '\n',folder_tags
                        if group_label:
                            try:
                                folder_groups[group_label].append(M2.hash)
                            except:
                                folder_groups[group_label] = [M2.hash]
                    else:
                        folder_tags = None # remember!

                    match = MOP.match_in_db(M2)
                    if not match: # new metadata
                        if folder_tags:
                            new_metadata.append(setM2tags(M2,sorted(folder_tags)))
                        else:
                            new_metadata.append(M2)
                    else: # known metadata (merge on folder_tags)
                        if folder_tags:
                            #merged_tags = set(getM2tags(M2) + folder_tags)
                            M2 = setM2tags(M2,sorted(folder_tags))
                            oldM2 = rec2M2(match)
                            #print 'match:', oldM2
                            old_metadata.append((oldM2,M2)) # (OLD,NEW)
                            #print '\nNew:',M2
                        else:
                            old_metadata.append((MOP.update(M2),None)) # (OLD,NEW)
                except KeyboardInterrupt:
                    clrln()
                    if really(' Cancel?', default=True): break
            clrln()

            # MERGE OLD+NEW HERE!

            total = pprc.reset(len(old_metadata))
            merged_metadata = list()
            for i,o_n in enumerate(old_metadata):
                spin(' Merging metadata... '+pprc.inc())
                if o_n[1]: # OLD->NEW
                    mergedM2 = MOP.merge_metadata(o_n[0], o_n[1], tags=bool(folder_tags), group=bool(folder_groups), new_filepath=True)
                    merged_metadata.append(mergedM2)
                    #print mergedM2
                    old_metadata[i] = None # to-delete after loop
                else: # OLD->None
                    old_metadata[i] = o_n[0]
            if merged_metadata:
                old_metadata = filter(None, old_metadata)
            clrln()

            # MERGE END.

            MOP.search_result = old_metadata + new_metadata + merged_metadata
            total = len(MOP.search_result)

            if total:
                cprint(' [i] '+str(total)+' files selected ('+str(len(new_metadata))+' new).')
            else:
                cprint(' [i] Directory is empty - aborting.')
                continue

            if new_metadata or merged_metadata:
                if not old_metadata or really(' Sub-select new items only?'):
                    MOP.search_result = new_metadata + merged_metadata
                    total = len(MOP.search_result)
                elif not new_metadata or really(' Sub-select known items only?'):
                    MOP.search_result = old_metadata + merged_metadata
                    total = len(MOP.search_result)
                    continue
                for i,M in enumerate(MOP.search_result):
                    if not M.rec:
                        #MOP.search_result[i] = MOP.save(M)
                        MOP.save(M,i)
                        #print '\nSave2:',M

                for hash_group in folder_groups.values():
                    if len(hash_group) < 2: continue # need at least two items to group
                    for hash in hash_group[1:]:
                        MOP.add_variant_by_hash(hash_group[0], hash)

                if folder_autotagged:
                    if new_metadata: cprint(' [*] Saved '+BRIGHT+str(len(new_metadata))+NORMAL+' new (auto-tagged)')
                    if merged_metadata: cprint(' [*] Merged '+BRIGHT+str(len(merged_metadata))+NORMAL+' (auto-tagged)')
                    if not buffer_mode: raw_input_buffer.append(kw.count[0]) # display tag count
                    MOP.update_tags()
                else:
                    cprint(' [*] Saved '+BRIGHT+str(len(new_metadata))+NORMAL+' new (tagless)')
            continue
        #0----------------------------------------------------------------------
        # USE raw AS COMMAND
        cmds = filter(None, raw.split())
        cmd = cmds.pop(0) if cmds else None
        #-----------------------------------------------------------------------
        # GLOBAL-COMMANDS
        #0----------------------------------------------------------------------
        if cmd in kw.runClipboard:
            clipboard = unicode(xerox.paste(),'utf-8')
            #print clipboard
            if clipboard:
                raw_input_buffer = [clipboard]+raw_input_buffer
            continue
        if cmd in kw.about:
            cprint('\n '+__nfr__+' '+__version__)
            cprint(' '+__website__)
            cprint(' '+__about__+'\n')
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.iterClipboard:
            clipboard = unicode(xerox.paste(),'utf-8').split(os.linesep)
            pattern = raw_fallback.replace('%clipboard%','%i%').replace('%CLIPBOARD%','%i%').replace('%clip%','%i%').replace('%CLIP%','%i%').replace('%ITER%','%i%').replace('%iter%','%i%').replace('%I%','%i%')
            print pattern
            for line in clipboard:
                if '%i%' not in pattern: break
                raw_input_buffer = [pattern.replace('%i%',line)]+raw_input_buffer
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.motd:
            if MOP.motd: cprint(motd_color_parser(MOP.motd))
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.db:
            #print 'AT:', os.getcwd()
            if not cmds or cmds[0] in kw.match:
                if not cmds and MOP.connected():
                    cprint(' [i] Current database location:\n '+BRIGHT+MOP.db.name+NORMAL+'\n')
                if database_locations:
                    if not determined_database_locations:
                        clrln(' [*] Determining database locations...')
                        determined_database_locations = get_buzhug_db_paths(database_locations)
                        if determined_database_locations:
                            determined_database_locations = tuple(map(friendly_relative_path, determined_database_locations))
                        clrln()
                    if determined_database_locations:
                        cprint(' [i] Determined database locations are:')
                        for i,path in enumerate(determined_database_locations):
                            if not cmds or cmds[1] in path:
                                if i%2:
                                    cprint(definition(' '+TINT+'('+BRIGHT+str(i+1)+NORMAL+')'+DULL,path))
                                else:
                                    cprint(definition(' '+TINT+'('+BRIGHT+str(i+1)+NORMAL+')'+DULL,BRIGHT+path+DULL))
                        complete.cmds = sorted(set(complete.cmds+list(determined_database_locations)))
                        readline.set_completer(complete.custom)
                        index = rawc_input(' Select database index to open? [cancel] ').strip()
                        if is_number(index):
                            index = abs(int(index.strip()))
                            if index <= len(determined_database_locations):
                                cmds = [determined_database_locations[index-1]]
                                # and execute as if normal command with path parameter...
                            else:
                                cprint(' [!] Index out of range [1..'+str(len(determined_database_locations))+'].')
                                continue
                        elif index.strip() in determined_database_locations:
                            cmds = [index.strip()]
                            # and execute as if normal command with path parameter...
                        else:
                            if not buffer_mode:
                                if index.strip():
                                    cprint(' [!] Expected index number or item.')
                                elif skippy:
                                    cprint(' [*] Skipped')
                            continue
                    else:
                        cprint(' [!] No database locations found.')
                        continue
                else: continue
                pathn = format_path(cmds[0]) # normalised
            else:
                pathn = format_path(' '.join(cmds)) # normalised

            #print 'DEFAULT:', pathn
            #print'AT:', os.getcwd()

            if not os.path.isabs(pathn): # always refer to a db by absolute path!
                #pathn = os.path.join(os.path.dirname(database_path), pathn)
                #pathn = os.path.join(os.getcwd(), pathn)
                pathn = os.path.realpath(pathn)
                #print 'ABSOL:', pathn

            filename = ntpath.basename(pathn)
            mode_index = 0

            if not os.path.exists(pathn):
                if not cmd_ln_mode and not really(' Create database?'): continue
                if not os.path.exists(os.path.dirname(pathn)):
                    os.makedirs(os.path.dirname(pathn))
                mode_index = 1
                cprint(' [*] Creating database: '+btint(filename))
            else:
                if not path_is_buzhug_db(pathn):
                    cprint(' [!] Such folder already exists - aborting.')
                    if not really(' Deploy database in that directory?'): continue
                    mode_index = 1
                    cprint(' [*] Creating '+btint(filename)+'.')
                    #continue
            clrln(' [*] Loading database...')
            if not cmd_ln_mode and MOP.db and MOP.db.name != pathn: # fancy horizontal marker on db change:
                clrln()
                horizontal_mark = list(':.'*(consoleX/2-1))
                random.shuffle(horizontal_mark)
                print '\n '+''.join(horizontal_mark)+'\n'
                clrln(' [*] Searching for databases...')

            MOP.motd = MOP.set_database(pathn, mode_index)

            if mode_index: # database was created
                #print 'FILE:', os.path.join(pathn,'run.nfr')
                with open(os.path.join(pathn,'run.nfr'),'w') as f: f.write(r'-d .')
                with open(os.path.join(pathn,'motd.txt'),'w') as f: f.write(r'')
                scripts_dir = os.path.join(pathn, 'scripts')
                os.makedirs(scripts_dir)
                #scripts_dir = pathn
                with open(os.path.join(scripts_dir,'setup-irfanview.nfr'),'w') as f: f.write(r'-d ..;;-a -p -save;-s {:};-make-filelist %HOME%\filelist;-x C:/Program Files/IrfanView/i_view32.exe | /thumbs | /filelist=%HOME%\filelist;-load')
                with open(os.path.join(scripts_dir,'setup-mpc.nfr'),'w') as f: f.write(r'-d ..;;-a -mpc -o {:} -x C:\Program Files\K-Lite Codec Pack\MPC-HC\mpc-hc.exe')
                with open(os.path.join(scripts_dir,'setup-foobar2000.nfr'),'w') as f: f.write(r'-d ..;;-a -fb -o {:} -x C:\Portable\foobar2000\foobar2000.exe')
                with open(os.path.join(scripts_dir,'setup-all.nfr'),'w') as f: f.write(r'-d ..;;setup-irfanview.nfr;setup-mpc.nfr;setup-foobar2000.nfr')

            if MOP.motd and not buffer_mode:
                clrln() # wipe indicator
                cprint(motd_color_parser(MOP.motd))
            DBA_NAME = os.path.basename(MOP.db.name)
            determined_database_locations = None
            if full_path_in_title:
                set_console_title(MOP.db.name+'{0}'+nfr_title)
            else:
                set_console_title(os.path.basename(MOP.db.name)+'{0}'+nfr_title)
            clrln()
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.wordnetDl:
            clrln(' [*] Downloading wordnet... ')
            if not use_wordnet:
                cprint(' [i] Set "'+BRIGHT+'use_wordnet'+NORMAL+'" in the config file to "'+BRIGHT+'yes'+NORMAL+'" to use tag similarity.')
            import nltk # http://www.nltk.org/
            nltk.download()
            clrln()
            continue
        if cmd in kw.cls:
            clear()
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.wordnetInfo and not buffer_mode:
            if wordnet_init:
                if use_wordnet:
                    cprint(' [i] Wordnet is activated.')
                else:
                    cprint(' [i] Wordnet is deactivated.')
            else:
                cprint(' [i] Wordnet was '+error_btint('not')+' initialized.')
            continue
        if cmd in kw.wordnetOff:
            use_wordnet = False
            if not buffer_mode and not wordnet_init:
                cprint(' [!] Wordnet was not initialized.')
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.wordnetOn:
            if not buffer_mode:
                if not wordnet_init:
                    cprint(' [!] Wordnet was not initialized.')
                continue
            use_wordnet = True
            continue
        #0----------------------------------------------------------------------
        if cmd.lower() == '-mp3hash':
            if using_mp3hash:
                cprint(' [i] Utilizing mp3hash.')
            else:
                cprint(' [i] Not in use.')
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.color:
            if cmds and cmds[0].strip().lower() in color_labels:
                for k,v in colors.iteritems():
                    if cmds[0].strip().lower() in k.split():
                        TINT = v
                        break
                ERRORT = Fore.MAGENTA if TINT==Fore.RED else Fore.RED
                BERRORT = Style.BRIGHT+Fore.MAGENTA if TINT==Fore.RED else Style.BRIGHT+Fore.RED
            else:
                unique_color_labels = [ k.split()[1] for k in sorted(colors.keys()) ]
                colored_labels = [get_color(label)+label+DULL for label in unique_color_labels]
                cprint(' [i] Available colors: '+' '.join(colored_labels)+'.')
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.cfg:
            cprint(' [i] Opening configuration file:\n '+BRIGHT+config_filepath+NORMAL)
            run_with_default_app(os.path.join(SCRIPT_DIR,config_filepath))
            continue
        #0----------------------------------------------------------------------
        if not MOP.connected():
            continue
        # SELECT ALL
        if cmd in _GLOBAL_KW_ and MOP.connected(): # M SELECTION (MOP.search_result)
            if cmd in kw.heal:
                #clrln(' [i] Please wait, healing the database...')
                if not cmds or cmds[0]=='empty': MOP.fix_empty()
                if not cmds or cmds[0]=='slashes':
                    MOP.fix_slashes()
                    clrln()
                if not cmds or cmds[0]=='duplicates': MOP.fix_duplicates()
                if not cmds or cmds[0]=='variants': MOP.fix_variants()
                if not cmds or cmds[0]=='db': MOP.fix_db()
                if not cmds or cmds[0]=='tags':
                    MOP.update_tags()
                    clrln()
                continue
            #1------------------------------------------------------------------
            total = len(MOP.search()) # SELECTION.select(MOP, verbose=False)
            all_tags = tuple( tag for M in MOP.search_result for tag in M.tags.split() )
            #1------------------------------------------------------------------
            if cmd == '**': # OUTDATED! TO VERIFY!
                clrln(' Verifying variant groups...')
                MOP.fix_variants()
                missing_files = list()
                for i,M2 in enumerate(MOP.search_result):
                    hash_ = (M2.hash+' ') if M2.hash else ''
                    spin(' Verifying all data... '+hash_+str(percent(i,total))+'%')
                    if M2file_is_missing(M2):
                        clrln()
                        #cprint(' [!] Missing: '+str(M2.hash))#, M.filepath
                        missing_files.append(M2)
                        MOP.show_info(M2, str(len(missing_files)), short=False)
                    #if cmd == '-all-untagged' and not M2.tags:
                    #    untagged_files.append(M2)
                if missing_files:
                    MOP.search_result = missing_files[:]
                    clrln(' [!] Incorrect data found and selected.')
                else:
                    clrln(' [i] All data is in place.')
                continue
            #1------------------------------------------------------------------
            if cmd == '-all-untagged':
                untagged_files = [M2 for M2 in MOP.search_result if not M2.tags]
                if untagged_files:
                    MOP.search_result = untagged_files
                    if addMode:
                        MOP.search_result = MOP.filter_duplicate_metadata(MOP.search_result+previous_search)
                    total = len(MOP.search_result)
                else:
                    cprint(' [!] Ignoring. All files are tagged.')
                continue
            #1------------------------------------------------------------------
            if not raw_input_buffer: # show summary on "search all" '*'
                #subtag = part2(raw) if part2(raw) in MOP.tags else None
                all_variant_hashes = sum( rec.variants.count(' ')+1 for rec in MOP.variant_db )
                if MOP.search_result:
                    total = len(MOP.search_result)
                    total_ideas = len([ M for M in MOP.search_result if M2is_remote(M,'idea') ])
                    total_phashed = sum( M.phash is not None for M in MOP.search_result )
                    db_stats = (
                        #(total, 'item' if total==1 else 'items'),
                        (total, ''),
                        (all_variant_hashes, 'variant' if all_variant_hashes==1 else '('+percent_str(all_variant_hashes,total)+'%) variants'),
                        (total_ideas, 'idea' if total_ideas==1 else '('+percent_str(total_ideas,total)+'%) ideas'),
                        (total_phashed, 'file phashed' if total_phashed==1 else '('+percent_str(total_phashed,total)+'%) files phashed')
                    )
                    db_stats = ', '.join( (' ' if e[1] else '').join((BRIGHT+str(e[0])+NORMAL,e[1])) for e in db_stats if e[0] )
                    print ''
                    cprint( tint('ITEMS: ')+db_stats+'.' )
                    if MOP.tags:
                        truncated_tags = [ part1(t,':') for t in all_tags ] # truncates tags at ":" sign
                        ansi_text = ' '.join(sorted_unique_average_bright(truncated_tags))
                        defin = tint('TAGS: ')
                        ansi_text = defin + ('\n'+' '*len(strip_esc(defin))).join(wrap(ansi_text, consoleX-1-len(strip_esc(defin))))
                        cprint(ansi_text)
                    if MOP.aliases:
                        truncated_aliases = [ part1(a,':')+':' if a.find(':')>0 else a for a in MOP.aliases ] # truncates aliases at ":" sign
                        cprint( ansi_definition(TINT+'ALIASES: '+DULL, ' '.join(sorted_unique_average_bright(truncated_aliases))) )
                    print ''
                else:
                    cprint(' [i] Database is void. Input `<url>` or `-i <text>` to add metadata.', markup=True)
            continue
        #0----------------------------------------------------------------------
        # SUB-SELECTION COMMANDS
        #0----------------------------------------------------------------------
        if cmd in kw.cpl('memSave memLoad memList'):
            if cmd in kw.memList:
                if not MOP.mem:
                    cprint(' [!] Nothing memorized. ('+BRIGHT+kw.aliases(cmd)[0]+NORMAL+')...')
                    continue
                print ''
                cprint(' [i] '+BRIGHT+str(len(MOP.mem))+NORMAL+' memorized selection(s):')
                cprint( btint('Index')+'\tItems\tLabel' )
                for i,(k, v) in enumerate(sorted(MOP.mem.items(), key=lambda e: e[1][2])):
                    #cprint(k, v)
                    if i%2:
                        cprint( TINT+'('+BRIGHT+str(i+1)+NORMAL+')\t'+DULL+'{'+str(len(v))+'}\t'+str(k) )
                    else:
                        cprint( BRIGHT+TINT+'('+str(i+1)+')\t'+DULL+BRIGHT+'{'+str(len(v))+'}\t'+str(k)+DULL )
                print ''
                continue
            k = part2(raw_fallback) if cmds else None # get load-label
            if cmd in kw.memSave:# and MOP.search_result:
                #MOP.mem = MOP.search_result[:]
                MOP.memSave(k, MOP.search_result[:])
            elif cmd in kw.memLoad and MOP.mem:
                #MOP.search_result = filter(None,( MOP.update(M,hash=False,create=False) for M in MOP.mem )) # update old selection
                memLoaded = MOP.memLoad(k)
                #if memLoaded:
                if addMode is None:
                    MOP.search_result = filter(None,( MOP.update(M,hash=False,create=False) for M in memLoaded )) # update old selection
                elif addMode:
                    MOP.search_result += filter(None,( MOP.update(M,hash=False,create=False) for M in memLoaded )) # update old selection
                    MOP.search_result = MOP.filter_duplicate_metadata(MOP.search_result)
                else: # add mode if False
                    hashes_to_delete = [e.hash for e in MOP.search_result if e.hash]
                    MOP.search_result = [e for e in MOP.search_result if not e.hash in hashes_to_delete]
                #else:
                #    cprint(' [!] Invalid label. Skipping ('+BRIGHT+kw.aliases(cmd)[0]+NORMAL+')...')
            #else:
            #    cprint(' [!] No content. Skipping ('+BRIGHT+kw.aliases(cmd)[0]+NORMAL+')...')
            #if cmds:
            #    raw_input_buffer[0:0] = [part2(raw_fallback)]
            continue
        #0----------------------------------------------------------------------
        if (cmd in ('+','-','=') and cmds and os.path.isfile(format_path(part2(raw_fallback)))) or addMode is not None and os.path.isfile(format_path(raw_fallback)):
            if addMode is None:
                filepath = format_path(part2(raw_fallback))
            else:
                filepath = format_path(raw_fallback)
            file_is_present_in_selection = hashfile(filepath) in [M.hash for M in MOP.search_result]
            if cmd in ('+',) or addMode:
                if not file_is_present_in_selection:
                    M2 = genM2(filepath=filepath) # hashes and phashes

                    db_match = MOP.match_in_db(M2)
                    if db_match:
                        if not buffer_mode: cprint(' [*] File added to selection.')
                        M2 = MOP.update(M2)
                        #M2 = rec2M2(db_match) # slightly faster than M2 = MOP.update(M2)
                    else:
                        if not buffer_mode: cprint(' [*] '+btint('New')+' file added to selection.')
                        M2 = MOP.save(M2)

                    MOP.search_result.append(M2)
                elif not buffer_mode:
                    cprint(' [!] This file is already selected.')
            elif cmd in ('-',) or addMode is False:
                if file_is_present_in_selection:
                    hash_to_delete = hashfile(filepath)
                    MOP.search_result = [e for e in MOP.search_result if e.hash != hash_to_delete]
                    if not buffer_mode:
                        cprint(' [*] File subtracted from selection.')
                elif not buffer_mode:
                    cprint(' [!] There is no such file.')
            continue
        #0----------------------------------------------------------------------
        # COLLECTION-MODE
        if cmd in kw.cpl('addModeNew defModeNew'):
            MOP.search_result[:] = list()
            cmd = kw.addMode[0] if cmd in kw.addModeNew else kw.defMode[0]
        if cmd in kw.addMode:
            addMode = True
            #cprint(' [i] Append mode set.')
            if cmds: raw_input_buffer[0:0]=[part2(raw_fallback)]
            continue
        if cmd in kw.cpl('subModeNew subMode'):
            addMode = False
            #cprint(' [i] Subtract mode set.')
            if cmds: raw_input_buffer[0:0]=[part2(raw_fallback)]
            continue
        if cmd in kw.defMode:
            addMode = None
            #cprint(' [i] Normal mode set.')
            if cmds: raw_input_buffer[0:0]=[part2(raw_fallback)]
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.rehash:
            if not MOP.search_result:
                cprint(' [!] Please select some files to rehash.')
                continue
            if (cmds and yN(cmds[0])) or really(' Re-hash '+BRIGHT+MOP.total()+NORMAL+' files?',n=' [*] Skipping' if skippy else None):
                if cmds:
                    if cmds[0].lower() in ('hashed',):
                        MOP.rehash(select_hashed=True, select_skipped=False)
                        continue
                    elif cmds[0].lower() in ('skipped',):
                        MOP.rehash(select_hashed=False, select_skipped=True)
                        continue
                MOP.rehash()
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.makeFilelist:
            if cmds:
                #filepath = os.path.expandvars(raw_fallback[len(cmd)+1:])
                filepath = format_path(part2(raw_fallback))
            else:
                filepath = os.path.join(HOME_DIR,'filelist') # default!
            filelist = [ os.path.realpath(M2.filepath) for M2 in MOP.search_result ]
            try:
                with open(filepath, 'w+') as f:
                    f.write('\n'.join(filelist).encode('utf8'))
            except:
                cprint(' [!] Error creating or opening filelist at '+BRIGHT+HOME_DIR)
                print_exception()
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.makeCollage: # race condition - fix it
            try:
                collage
            except:
                continue
            filepaths, labels = (list(), None)
            for M2 in MOP.search_result:
                if os.path.exists(M2.filepath) and M2.phash: filepaths.append(os.path.realpath(M2.filepath))
            if cmds:
                try: size = float(cmds[0])
                except: size = None
            else:
                size = None
            #print filepaths
            filepath = os.path.join(HOME_DIR,'nfr_collage.jpg')
            #filepath = r'nfr_collage.jpg'
            try:
                collage.make_collage(filepaths, filepath, labels=labels, size=size)
                cprint(' [i] Collage saved as: "'+filepath+'"')
                sleep(post_subprocess_delay)
                run_with_default_app(filepath)
                sleep(post_subprocess_delay)
            except:
                cprint(' [!] Could not create collage.')
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.count:
            tags = ()
            for M2 in MOP.search_result:
                #M2 = M2debug_tags(M2)#why?
                if cmds:
                    new_tags = tuple( tag for tag in getM2tags(M2) if any( match.lower() in tag.lower() for match in cmds ) )
                else:
                    new_tags = tuple(getM2tags(M2))
                tags += new_tags
            if not tags:
                cprint(' [!] No tags to count.')
                continue
            uniques = tuple(set(tags))
            amount__tags = list()
            selection_total = 0
            for unique in uniques:
                amount = tags.count(unique)
                amount__tags.append((amount, unique))
                selection_total += amount
            amount__tags.sort(reverse=True)
            print ''
            print definition(TINT+'TAGS:'+DULL, ' '.join( map(lambda x:x[1]+(BRIGHT if x[0]>= len(MOP.search_result) else '')+TINT+'('+str(x[0])+')'+DULL, amount__tags) ), width=consoleX-1)
            #txt= definition(TINT+'TAGS:'+DULL, ' '.join( map(lambda x:x[1]+'('+str(x[0])+')', amount__tags) ))
            cprint(' [i] '+BRIGHT+str(selection_total)+NORMAL+' tags in selection, '+BRIGHT+str(len(uniques))+NORMAL+' unique. Diversity ratio: '+BRIGHT+str(round(float(selection_total)/len(uniques),2))+NORMAL+'.\n')
            continue
        #0----------------------------------------------------------------------
        if cmd in kw.remove:
            if not MOP.search_result:
                cprint(' [!] Nothing there to remove.')
                continue
            removed = 0
            if really(' Remove '+BRIGHT+str(MOP.total())+NORMAL+' metadata entries? (files will remain)'):
                for M2 in MOP.search_result:
                    removed += MOP.remove(M2)
                if removed:
                    MOP.update_tags()
                    MOP.search_result = list(); total = 0
                    cprint(' [*] Removed')
                else:
                    cprint(' [!] Could not remove.')
            continue
        #0----------------------------------------------------------------------
        if cmd in _SUBSELECTION_KW_ or cmd in kw.clipb2img: # copies / moves files from Search results to specified dst
            #1------------------------------------------------------------------
            if cmd in kw.c: # kw.copy
                full_filepath = 'f' in cmds or 'full' in cmds # !obscure, hidden functionality!
                if full_filepath:
                    try:
                        cmds.remove('f')
                        cmds.remove('full')
                    except: pass
                selection = slice_select_metadata(MOP.search_result, cmds)
                copy_buffer = list()
                for M2 in selection:
                    if M2is_remote(M2,'idea'):
                        copy_buffer.append(M2.filepath[5:])
                    elif M2is_remote(M2):
                        copy_buffer.append(M2.filepath)
                    else:
                        if full_filepath:
                            copy_buffer.append(os.path.abspath(M2.filepath))
                        else:
                            copy_buffer.append(M2.filepath)
                if copy_buffer:
                    #print  '[D] '+'\n'.join(copy_buffer[:])
                    xerox.copy(str('\n'.join(copy_buffer)))
                    if len(copy_buffer) > 1:
                        cprint(' [*] Copied '+BRIGHT+str(len(copy_buffer))+NORMAL+' items to clipboard.')#, '"'+full_filepath+'"'
                    else:
                        cprint(' [*] Copied item to clipboard.')
                else:
                    cprint(' [!] Nothing to copy.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.ch:
                separator = None
                for i,c in enumerate(cmds):
                    if c and not is_slice(c):
                        separator = c[:]
                        cmds[i] = None
                cmds = filter(None, cmds)
                selection = slice_select_metadata(MOP.search_result, cmds)
                hashes = [ M2.hash for M2 in selection if M2.hash ]
                total = len(hashes)
                if not hashes:
                    cprint(' [!] No hash to be found.')
                    continue
                if separator: # ie: "-ch |" adds a " | " between every hash
                    xerox.copy(str((' '+separator+' ').join(hashes)))
                else:
                    xerox.copy(str('\n'.join(hashes)))
                if total > 1:
                    cprint(' [*] '+BRIGHT+str(total)+NORMAL+' '+default_algo.__name__+' hashes copied to clipboard.')
                else:
                    cprint(' [*] '+default_algo.__name__+' hash copied to clipboard.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.cpl('ct ctSplit'):
                selection = slice_select_metadata(MOP.search_result, cmds)
                tags = ( getM2tags(M2) for M2 in selection if M2.tags )
                tags = set().union(*tags)
                if not tags:
                    cprint(' [!] No tags to copy.')
                    continue
                unique = sorted(tags)
                total = len(unique)
                if not cmd in kw.ctSplit:
                    unique = slash_join_tags(unique)
                xerox.copy(str(' '.join(unique)))
                cprint(' [*] Copied '+BRIGHT+str(total)+NORMAL+' unique tag(s) to clipboard.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.cpl('cm'):
                selection = slice_select_metadata(MOP.search_result, cmds)
                ret = ''
                total = len(selection)
                copied = 0
                for i,M2 in enumerate(selection):
                    spin(' Copying metadata to clipboard... '+str(percent(i,total))+'%')
                    copied += 1
                    ret += M2.filepath + ';'
                    if M2.tags:
                        unique = sorted(getM2tags(M2))
                        if not cmd in kw.ctSplit:
                            unique = slash_join_tags(unique)
                        ret += '-e ' + ' '.join(unique) + ';'
                    if M2.hash:
                        #print M2.hash
                        hash_variants = MOP.hash_variants_by_hash(M2.hash)#.split() # space separated hashes
                        if hash_variants: # orginal_hash & other_space_separated_hashes
                            #hash_variants.remove(M2.hash)
                            hash_variants = part2(hash_variants).replace(' ',';')
                            ret += '++ ' + hash_variants + ';==;-g;'
                ret = ret.rstrip(';')
                clrln()
                if ret:
                    xerox.copy(str(ret))
                    cprint(' [*] Copied '+BRIGHT+str(copied)+NORMAL+' unique metadata to clipboard.')
                continue
            #0------------------------------------------------------------------
            if cmd in kw.export:
                if not MOP.search_result:
                    cprint(' [!] Please select some items to export.')
                    continue
                if not cmds:
                    cprint(' [!] Please specify the path to export to.')
                    continue
                filepath = format_path(part2(raw))
                if not os.path.exists(filepath) or really(' Overwrite?',n=' [*] Skipped'):
                    path = os.path.dirname(filepath)
                    if path and not os.path.exists(path):
                        try:
                            os.makedirs(path)
                        except:
                            cprint(' [!] Error creating directory '+BRIGHT+path)
                            print_exception()
                    try:
                        with open(filepath, 'w') as f:
                            f.write('# created at '+str(datetime.datetime.now())+'\n===\n')
                            unique_hashes = set()
                            for M2 in MOP.search_result:
                                #if M2.hash:
                                #    unique_hashes.add(M2.hash)
                                #    f.write('-hash '+M2.hash) # variation groups?
                                #    if M2.tags:
                                #        f.write(';-e '+' '.join(getM2tags(M2))+'\n')
                                #    else:
                                #        f.write('\n')
                                #elif M2.filepath:
                                if M2.filepath:
                                    f.write(M2.filepath)
                                    if M2.tags:
                                        f.write(';-e '+' '.join(getM2tags(M2))+'\n')
                                    else:
                                        f.write('\n')
                            unique_hashes = sorted(unique_hashes)
                            total = len(unique_hashes)
                            while unique_hashes:
                                spin(' Exporting hash groups... '+str(percent(len(unique_hashes),total))+'%'+'\t('+str(len(unique_hashes))+' left)  ')
                                group = MOP.hash_variants_by_hash(unique_hashes[0])
                                del unique_hashes[0]
                                if group:
                                    group = sorted(group.split())
                                    for hash in group:
                                        if hash in unique_hashes:
                                            unique_hashes.remove(hash) # remove grouped items from being re-researched
                                        else:
                                            group.remove(hash) # file without reference, excluded from group
                                    if len(group) > 1:
                                        #cprint(' [D] '+' '.join(group))
                                        f.write('+++;')
                                        for hash in group:
                                            f.write(hash+';')
                                        f.write('-g\n')
                            f.write('===')
                            clrln()
                    except IOError as e:
                        cprint(' [!] Error writing "'+filepath+'"!')
                        print e
                continue
            #1------------------------------------------------------------------
            if cmd in kw.shuffle:
                random.shuffle(MOP.search_result)
                if not buffer_mode: cprint(' [*] Shuffled')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.sort:
                M2_sort_nicely(MOP.search_result)
                if not buffer_mode: cprint(' [*] Sorted')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.reverse:
                #M2_sort_nicely(MOP.search_result, reverse=True)
                MOP.search_result = MOP.search_result[::-1]
                if not buffer_mode: cprint(' [*] Order reversed')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.x:
                run_cmd = raw[len(cmd)+1:]
                if '-s' in run_cmd.split():
                    metadata_list = slice_select(MOP.search_result,part2(run_cmd,'-s'))
                    run_cmd  = part1(run_cmd,'-s')
                    filelist = [ os.path.realpath(M2.filepath) for M2 in metadata_list ]
                else:
                    filelist = list()
                run_cmds = run_cmd.split()
                # expand special enviromental path variables like %HOMEPATH%
                run_cmd = ' '.join(
                    [ '='.join(
                        [ os.path.expandvars(a) if os.path.isfile(os.path.expandvars(a)) else a for a in x.split('=') ]
                        ) for x in run_cmds ]
                    )
                run_cmds = [ expandvars_nfr(x.strip()) for x in run_cmd.split('|')+filelist ]
                #print '[D]', run_cmds
                try:
                    subprocess.Popen(run_cmds, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
                except:
                    cprint(' [!] Error running '+BRIGHT+'\n '.join(run_cmds))
                    print_exception()
                continue
            #1------------------------------------------------------------------
            if cmd in kw.browse:
                if cmds and os.path.isdir(part2(raw)) and os.path.exists(part2(raw)):
                    run_with_default_app(part2(raw))
                    continue
                if not MOP.search_result:
                    #if not buffer_mode: cprint(' [i] Opening current working directory.')
                    #run_with_default_app(os.getcwd())
                    if not buffer_mode: cprint(' [i] Opening current database location.')
                    run_with_default_app(MOP.db.name)
                    continue
                if cmds and is_number(cmds[0]):
                    index = int(cmds[0]) - 1
                else:
                    index = 0
                filepath = MOP.search_result[index].filepath
                if filepath.startswith('idea:'):
                    filepath = filepath[5:]
                if os.path.exists(filepath):
                    # the file/directory exists
                    if not os.path.isdir(filepath):
                        path = os.path.dirname(filepath)
                    else:
                        path = filename
                    run_with_default_app(path) # browse
                elif os.path.isfile(filepath) and os.path.exists(os.path.dirname(filepath)):
                    # file is misplaced but directory exists
                    path = os.path.dirname(filepath)
                    if os.path.isdir(path):
                        run_with_default_app(path) # browse
                    else:
                        cprint(' [!] Can\'t browse directory: '+BRIGHT+path)
                #if os.path.isdir(path) and os.path.exists(path):
                #    #subprocess.Popen((path,), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
                #
                else:
                    cprint(' [!] Can\'t browse: '+BRIGHT+path)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.open:
                app = None
                multi_selection = None
                if not cmds:
                    Ms_to_open = MOP.search_result[:1]
                else:
                    if '-s' in cmds: # this will overwrite any previous selection (handy in some alias cases)
                        indexes = cmds.index('-s')
                        multi_selection = slice_select(MOP.search_result,' '.join(cmds[indexes+1:]))
                        cmds = cmds[:indexes]
                    #Ms_to_open = list()
                    slices = list()
                    for i,c in enumerate(cmds):
                        if c in ('-x','x', '-with','with'):
                            app = ' '.join(cmds[i+1:])
                            if app in MOP.aliases:
                                match = MOP.alias_db.select(alias=unicode(app))
                                if match:
                                    app = match[0].selection
                                    break
                            app = unicode(format_path(' '.join(cmds[i+1:])))
                            break
                        else:
                            slices.append(c)
                    if multi_selection:
                        Ms_to_open = multi_selection # overwriting with the '-s' selection
                    else:
                        Ms_to_open = slice_select(MOP.search_result, ' '.join(slices)) if slices else MOP.search_result[:1]
                    # filter out all filepathless, displaced and ideas:
                    Ms_to_open = filter(lambda x:x.filepath, Ms_to_open) # exclude filepathless
                    Ms_to_open = filter(lambda x:not (x.filepath.startswith('idea:') and not os.path.isfile(x.filepath[5:])), Ms_to_open) # exclude text ideas
                if Ms_to_open: # local url in filepath (or idea:url)
                    urls = map(lambda x:os.path.realpath(x.filepath.replace('idea:','',1)) if not M2is_remote(x) else x.filepath, Ms_to_open) # get local absolute filepaths
                    if app:
                        if (not os.path.isfile(app)) or (not is_exe(app)):
                            app = which(app)
                        if app:
                            #print ' [*] Opening with "'+app+'"...'
                            #urls = map(expandvars_nfr, urls)
                            urls = [ url if os.path.exists(url) else expandvars_nfr(url) for url in urls ]
                            system_cmd = tuple([app] + urls)
                            #print system_cmd
                            try:
                                subprocess.Popen(system_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                                sleep(post_subprocess_delay)
                            except:
                                cprint(' [!] Error while opening selection using '+BRIGHT+'\n '.join(system_cmd))
                                print_exception()#' [!] Error while openinig selection.')
                            continue
                        else:
                            pass # handle error by system
                    if not buffer_mode:
                        clrln(' Opening url (using OS default)...')
                    if urls[0].startswith('idea:') and os.path.exists(format_path(urls[0][5:].strip())):
                        urls[0] = format_path(urls[0][5:].strip())

                        #cprint(' [i] Idea is a valid filepath. '+ urls[0])
                    if os.path.exists(urls[0]):
                        try:
                            #print '\nrunning:', (urls[0],), '\n'
                            run_with_default_app(urls[0])
                        except:
                            cprint(' [!] Error running (by OS) '+BRIGHT+urls[0])
                            print_exception()
                    else:
                        expanded = expandvars_nfr(urls[0])
                        if os.path.exists(expanded):
                            try:
                                #print '\nexpanded to:', (expanded,), '\n'
                                run_with_default_app(expanded)
                            except:
                                cprint(' [!] Error running (by OS) '+BRIGHT+expanded)
                                print_exception()
                        else:
                            try:
                                #print '\nrunning expanded:', (urls[0],), '\n'
                                run_with_default_app(urls[0])
                            except:
                                cprint(' [!] Error running (by OS) '+BRIGHT+'\n '.join(urls[0]))
                                print_exception()
                    sleep(post_subprocess_delay)
                    if not buffer_mode:
                        clrln() # clear the "opening file" indicator
                else:
                    cprint(' [!] Nothing to open.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.local:
                MOP.search_result = [ M2 for M2 in MOP.search_result if os.path.isfile(M2.filepath) ]
                total = len(MOP.search_result)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.remote:
                MOP.search_result = [ M2 for M2 in MOP.search_result if M2is_remote(M2) ]
                total = len(MOP.search_result)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.links:
                MOP.search_result = [ M2 for M2 in MOP.search_result if M2is_remote(M2) and not M2is_remote(M2,'idea') ]
                total = len(MOP.search_result)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.ideas:
                MOP.search_result = [ M2 for M2 in MOP.search_result if M2is_remote(M2,'idea') ]
                total = len(MOP.search_result)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.inverse:
                clrln(' Inverting selection...')
                old_selection_hash_list = [ M2.hash for M2 in MOP.search_result ]
                all_metadata = MOP.search()#SELECTION.select(MOP, verbose=False)
                MOP.search_result = [M2 for M2 in all_metadata if M2.hash not in old_selection_hash_list]
                total = len(MOP.search_result)
                clrln()
                if not buffer_mode:
                    cprint(' [*] Selection inverted')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.group:
                if cmds: # -group "asd/cxz qwe.ext"
                    filepath = format_path(part2(raw).strip())
                    if os.path.isfile(filepath):
                        M2 = MOP.update(genM2(filepath=filepath))
                        MOP.search_result.append(M2)
                        MOP.search_result = MOP.filter_duplicate_metadata()
                    else:
                        cprint(' [!] Filepath is incorrect.')
                        continue
                hashes = [ M2.hash for M2 in MOP.search_result if M2.hash ]
                #print hashes
                if len(hashes) > 1:
                    variants_count = 0
                    for hash in hashes[1:]:
                        count = MOP.add_variant_by_hash(hashes[0], hash)
                        if count > variants_count:
                            variants_count = count
                    if not buffer_mode:
                        cprint(' [*] Grouped '+BRIGHT+str(variants_count)+NORMAL+'.')
                else:
                    cprint(' [!] Select hashable items to group.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.ungroup:
                if cmds:
                    filepath = format_path(part2(raw).strip())
                    if os.path.isfile(filepath):
                        hash_to_ungroup = hashfile(filepath)
                        for i,M2 in enumerate(MOP.search_result):
                            spin(' Ungrouping... '+str(percent(i,total))+'%')
                            MOP.remove_variant_by_hash(hash_to_ungroup)
                            if not buffer_mode:
                                clrln(' [*] File removed from group.')
                            else:
                                clrln()
                    else:
                        cprint(' [!] The specified filepath is invalid.')
                elif MOP.search_result:
                    hashes_to_ungroup = [ M2.hash for M2 in MOP.search_result if M2.hash ]
                    for hash in hashes_to_ungroup:
                        spin(' Ungrouping... '+str(percent(i,len(hashes_to_ungroup)))+'%')
                        MOP.remove_variant_by_hash(hash)
                    if hashes_to_ungroup:
                        if not buffer_mode:
                            clrln(' [*] '+BRIGHT+str(len(hashes_to_ungroup))+NORMAL+' file(s) removed from group.')
                        else:
                            clrln()
                else:
                    cprint(' [i] Removes file variant from it\'s group (specified by a file).')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.cpl('variants variantsAdd variantsSub'):
                if not MOP.search_result:
                    cprint(' [!] Pre-select some files to select their variants.')
                    continue
                if cmd in kw.variantsSub: # truncate selection by variants
                    for i,M2 in enumerate(MOP.search_result):
                        spin(' Filtering-out grouped variants... '+str(percent(i,total))+'%')
                        if M2.hash and MOP.hash_variants_by_hash(M2.hash):
                            MOP.search_result[i] = None
                    MOP.search_result = filter(None,MOP.search_result)
                else:
                    metadata_variants = list()
                    for i,M2 in enumerate(MOP.search_result):
                        spin(' Searching variants... '+str(percent(i,total))+'%')
                        if M2.hash:
                            M2s = MOP.get_metadata_variants_by_hash(M2.hash)
                            if M2s:
                                metadata_variants.extend(M2s)
                    clrln(' Finishing...')
                    if cmd in kw.variantsAdd: # expand selection by variants
                        MOP.search_result = MOP.search_result + filter(None,metadata_variants)
                        #MOP.search_result = MOP.search_result + metadata_variants
                    else: # variants only
                        MOP.search_result = filter(None,metadata_variants)
                        #MOP.search_result = metadata_variants
                    MOP.search_result = MOP.filter_duplicate_metadata()
                    #M2_sort_nicely(MOP.search_result)
                total = len(MOP.search_result)
                clrln()
                continue
            #1------------------------------------------------------------------
            if cmd in kw.cpl('over less equal') and MOP.search_result:
                if not cmds:
                    cprint(' [!] Please specify the tag amount to filter.')
                    continue
                try:
                    amount = int(cmds[0])
                except ValueError:
                    cprint(' [!] Invalid tag amount specified for \''+BRIGHT+cmd+NORMAL+'\'.')
                    continue
                metadata_tuples = list()
                if cmd in kw.over:
                    for i,M in enumerate(MOP.search_result):
                        spin(' Searching... '+str(percent(i,total))+'%')
                        if len(getM2tags(M)) > amount:
                            metadata_tuples.append((len(getM2tags(M)), M))
                elif cmd in kw.less:
                    for i,M in enumerate(MOP.search_result):
                        spin(' Searching... '+str(percent(i,total))+'%')
                        if len(getM2tags(M)) < amount:
                            metadata_tuples.append((len(getM2tags(M)), M))
                elif cmd in kw.equal:
                    for i,M in enumerate(MOP.search_result):
                        spin(' Searching... '+str(percent(i,total))+'%')
                        if len(getM2tags(M)) == amount:
                            metadata_tuples.append((len(getM2tags(M)), M))
                clrln()
                metadata_tuples.sort()
                MOP.search_result = [e[1] for e in metadata_tuples]
                if addMode: MOP.search_result = MOP.filter_duplicate_metadata(MOP.search_result+previous_search)
                total = len(MOP.search_result)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.edit:
                if cmds:
                    m_t = MOP.modify_metadata_list(MOP.search_result, ' '.join(cmds), verbose=not buffer_mode)
                    if m_t:
                        MOP.update_tags()
                        if not buffer_mode:
                            cprint(' [i] Modified '+BRIGHT+str(m_t[0])+NORMAL+' metadata ('+BRIGHT+str(m_t[1])+NORMAL+' tags).')
                    elif not buffer_mode:
                        cprint(' [i] Nothing was modified.')
                elif not buffer_mode:
                    cprint(' [!] Please input some tags. **-** to add, **+** to remove.', markup=1)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.dir:
                if not cmds:
                    if not MOP.search_result:
                        cprint(' [!] Select some files to display distribution by location.')
                        continue
                    cprint(' [i] Locations of '+BRIGHT+MOP.total()+NORMAL+' selected items are:')
                    dirs = list()
                    for i,M2 in enumerate(MOP.search_result):
                        spin(' Researching... '+str(percent(i,total))+'%')
                        if M2.filepath:
                            dirs.append(os.path.dirname(M2.filepath))
                    clrln()
                    uniques = sorted_unique(dirs)
                    uniques = filter(lambda u:not filepath_is_remote(u), uniques) # no remote url's
                    additional_completions = uniques[:]
                    for i,unique in enumerate(uniques):
                        uniques[i] = (unique, dirs.count(unique))
                    print ''
                    cprint( btint('Index')+'\tItems\tDirectory' )
                    for i,dir in enumerate(uniques):
                        if not dir[0]:
                            dir = ('TEXT / IDEA',dir[1]) if dir[1] == 1 else ('TEXT / IDEAS',dir[1])
                        #cprint( TINT+'('+BRIGHT+str(i+1)+NORMAL+') '+DULL+'{'+str(dir[1])+'} '+dir[0] )
                        if i%2:
                            cprint( TINT+'('+BRIGHT+str(i+1)+NORMAL+')\t'+DULL+'{'+str(dir[1])+'}\t'+dir[0] )
                        else:
                            cprint( BRIGHT+TINT+'('+str(i+1)+')\t'+DULL+BRIGHT+'{'+str(dir[1])+'}\t'+dir[0]+DULL )
                    print DULL
                    if len(uniques) < 2: # single dir - nothing to select.
                        continue
                    slices = rawc_input(' Sub-select items by directory index? [no] ').strip()
                    if slices and is_slice(part1(slices)):
                        uniques = [ u[0] for u in uniques ] # (<filepath>, <fileAmout>) -> <filepath>
                        selected_dirs = slice_select(uniques, slices) # exact path string
                        subselect = list()
                        for i,M2 in enumerate(MOP.search_result):
                            spin(' Researching... '+str(percent(i,total))+'%')
                            if os.path.dirname(M2.filepath) in selected_dirs:
                                subselect.append(M2)
                        clrln()
                        if subselect:
                            MOP.search_result = subselect
                            total = len(MOP.search_result)
                        else:
                            cprint(' [!] No matching items (from selection) found.')
                        continue
                    elif slices:
                        raw_input_buffer.append(slices) # probably command given
                        continue
                else:
                    path = format_path(' '.join(cmds))
                    subselect = list()
                    for i,M in enumerate(MOP.search_result):
                        spin(' Researching... '+str(percent(i,total))+'%')
                        if os.path.realpath(os.path.dirname(M2.filepath)) == os.path.realpath(path):
                            subselect.append(M2)
                    clrln()
                    if subselect:
                        MOP.search_result = subselect
                        total = len(MOP.search_result)
                    else:
                        cprint(' [!] No matching items (from selection) found.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.cpl('list listMore listMore2 listLess'):#('-list','-l', '-list+','-l+', '-l-','-list-'):
                sub_selection = MOP.search_result if not cmds else slice_select(MOP.search_result, ' '.join(cmds))
                if not sub_selection:
                    cprint(' [!] Nothing to list.')
                    continue
                print ''
                #for i,M in enumerate(sub_selection):
                #    total_filesize = 0
                #    try:
                #        with open(M.filepath,'rb') as f:
                #            total_filesize += len(f.read())/1024
                #    except:
                #        pass
                #        #print len(f.read())/1024, 'KB'
                #small_selection = True if total_filesize < 1024**3 else False
                for i,M in enumerate(sub_selection):
                    try:
                        if sub_selection is MOP.search_result:
                            title = str(i+1) if len(sub_selection) > 1 else None
                        else:
                            title = str(MOP.search_result.index(M)+1)
                        if cmd[-1] == '+':
                            hashes = True if cmd in kw.listMore2 else False
                            MOP.show_info(M, title, short=False, hashes=hashes)
                        elif cmd[-1] == '-':
                            #MOP.show_info(M, str(i+1))
                            if M.filepath and M.filepath.startswith('idea:'):
                                if os.path.isfile(M.filepath[5:]):
                                    # url as idea:
                                    cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', DULL+'idea/URL: '+btint(M.filepath.replace('idea:',''))) )
                                else:
                                    # idea with markup:
                                    cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', DULL+M.filepath.replace('idea:','')), markup=True )
                            elif M.filepath:
                                # not idea (remote url or local file):
                                if M2is_remote(M):
                                    cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', DULL+M.filepath) )
                                elif os.path.exists(M.filepath):
                                    cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', DULL+os.path.basename(M.filepath)) )
                                else:
                                    cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', error_tint(os.path.dirname(M.filepath)+os.sep)+error_btint(os.path.basename(M.filepath))) )
                            elif M.hash:
                                cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', error_tint('nameless item '+BRIGHT+M.hash+NORMAL)) )
                            else:
                                cprint( definition(TINT+'('+BRIGHT+str(i+1)+NORMAL+')', error_tint('nameless item')) )
                        else:
                            MOP.show_info(M, title, hash=False, modified=False)
                        #if not small_selection:
                        #    cprint('\n [i] No hash check was performed since selection\'s filesize is too big.')
                    except KeyboardInterrupt:
                        if really(' Cancel?', default=True): break
                print ''
                continue
            #1------------------------------------------------------------------
            if part1(raw_fallback) in kw.alias:
                cmds = raw_fallback.split()[1:]
                if cmds:
                    MOP.update_tags()
                    if cmds[0] in MOP.tags:
                        cprint(' [!] Collides with tag. Try a different name.')
                        continue
                    if cmds[0] in reserved + _ALL_KW_:
                        cprint(' [!] Reserved word ('+BRIGHT+cmds[0]+NORMAL+'). Try a different name.')
                        continue
                    match = MOP.alias_db.select_for_update(alias=unicode(cmds[0]))
                    if len(cmds) > 1:
                        alias_expanded = ' '.join(cmds[1:])
                        if cmds[0] == alias_expanded:
                            cprint(' [!] I can see forever!!')
                            continue
                        if os.path.isfile(format_path(alias_expanded)): # leave "' quotes for executables with params only
                            alias_expanded = format_path(alias_expanded)
                    else:
                        alias_expanded = unalias_list(cmds[:1],False)[0] if use_aliases else cmds[:1][0]
                        if alias_expanded == cmds[0]:
                            cprint(' [!] Unknown alias: "'+alias_expanded+'".')
                        else:
                            cprint(definition(' [i] '+TINT+'ALIAS:'+DULL, alias_expanded))
                        continue

                    if not match:
                        if not buffer_mode:
                            cprint(' [*] Creating alias: '+BRIGHT+cmds[0]+NORMAL)
                        record_id = MOP.alias_db.insert(alias=unicode(cmds[0]), selection=unicode(alias_expanded))
                        MOP.modified = True # flag database modification
                    else: # update db record
                        if not buffer_mode:
                            cprint(' [*] '+ERRORT+'Overwriting'+DULL+' alias: '+BRIGHT+cmds[0]+NORMAL)
                            #cprint(definition(' [i] '+TINT+'PREV:'+DULL, unalias(cmds[0])))
                        match[0].update(alias=unicode(cmds[0]), selection=unicode(alias_expanded))
                    MOP.update_aliases() # update database snapshot (new aliases need an update!)
                    if not buffer_mode:
                        #cprint(definition(' [i] Extends to:', alias_expanded))
                        #cprint(' [i] Alias: '+str(unalias(cmds[0])))
                        cprint(definition(' [i] '+TINT+'ALIAS:'+DULL, unalias(cmds[0])))
                else:
                    MOP.update_aliases()
                    if MOP.aliases:
                        truncated_aliases = [a.split(':').pop(0)+':'*(':' in a) for a in MOP.aliases] # truncates aliases at ":" sign
                        cprint( definition(TINT+'ALIASES:'+DULL,' '.join(sorted_unique(truncated_aliases))) )
                    else:
                        cprint(' [i] No aliases defined.')
                continue
            #1------------------------------------------------------------------
            if part1(raw_fallback) in kw.aliasRemove:
                cmds = raw_fallback.split()[1:]
                if cmds:
                    match = MOP.alias_db.select(alias=unicode(cmds[0]))
                    if match:
                        MOP.alias_db.delete(match)
                        MOP.modified = True # flag database modification
                        MOP.aliases.remove(cmds[0])
                        cprint(' [*] '+ERRORT+'Removed'+DULL+' alias '+BRIGHT+cmds[0]+NORMAL)
                else:
                    cprint(' [i] Usage: '+help.usage2(kw.aliasRemove,' <alias-to-remove>'), markup=True)
                    truncated_aliases = [a.split(':').pop(0)+':'*(':' in a) for a in MOP.aliases] # truncates aliases at ":" sign
                    cprint( definition(TINT+'ALIASES:'+DULL, ' '.join(sorted_unique(truncated_aliases))) )
                continue
            #1------------------------------------------------------------------
            if cmd in kw.cpl('RMDF RMDFx'):
                path = format_path(part2(raw_fallback))
                if path.lower() in forbidden_dirs and not really(' This directory is probably not safe to filter. Are you sure?'):
                    cprint(' [i] Please be careful...')
                    continue
                if cmd in kw.RMDFx:
                    if not really(' Delete permanently? Are you sure?'): continue
                    else:
                        removed_out_of = remove_duplicate_files(path.split(' -ext ', 1), undo=False)
                else:
                    removed_out_of = remove_duplicate_files(path.split(' -ext ', 1))
                percentage = 0 if removed_out_of[1]==0 else int(float(removed_out_of[0]) / removed_out_of[1] * 100)
                cprint(' [*] Preserved ' + str(removed_out_of[0]) + '/' + str(removed_out_of[1]) + ' ('+str(percentage)+'%) unique files.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.clipb2img: # does not recognize partial matches - to fix
                im = ImageGrab.grabclipboard()
                im.save(os.path.join(HOME_DIR,'nfr_clipboard_image.png'),'PNG')
                MOP.search_result = [genM2(os.path.join(HOME_DIR,'nfr_clipboard_image.png'), phash=imhash_im_object(im))]
                #print 'PHASH:', imhash_im_object(im), MOP.search_result[0]
                continue
            #1------------------------------------------------------------------
            if not MOP.search_result:
                if not cmd in kw.cpl('similar pSimilar similarFuz pSimilarFuz'): # <- parameters allowed
                    cprint(' [!] Nothing selected.')
                    continue
            #1------------------------------------------------------------------
            if cmd in kw.rename:
                total = pprc.reset(len(MOP.search_result))
                if len(cmds) == 1: # remove tag
                    if not really(' Really remove '+BRIGHT+cmds[0]+NORMAL+' tag from '+BRIGHT+str(total)+NORMAL+' selected items?'):
                        cprint(' [*] Skipping')
                        continue
                    removed = 0
                    for i,M in enumerate(MOP.search_result):
                        spin(' Removing... '+pprc.inc())
                        if cmds[0] in getM2tags(M):
                            M = M2rem_tag(M,cmds[0])
                            M = MOP.save(M,i)
                            removed += 1
                    clrln()
                    if removed:
                        MOP.update_tags() # memorize
                    cprint(' [*] Removed '+BRIGHT+str(removed)+NORMAL+' tags.')
                    continue
                elif len(cmds) == 2: # rename tag
                    renamed = 0
                    for i,M in enumerate(MOP.search_result):
                        spin(' Renaming... '+pprc.inc())
                        if cmds[0] in getM2tags(M):
                            M = M2rename_tag(M, cmds[0], cmds[1])
                            M = MOP.save(M,i)
                            renamed += 1
                    if renamed:
                        MOP.update_tags() # memorize
                    clrln(' [*] Renamed '+BRIGHT+str(renamed)+NORMAL+' tags.\n')
                else:
                    cprint(' [i] Usage:', help.usage2(kw.rename,' <old-tag> <new-tag>')+'\n [i] Renames all tags from the preselected files.', markup=True)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.renameMatchingGroup:
                if len(cmds) > 1: # rename
                    total = pprc.reset(len(MOP.search_result))
                    modified = 0
                    renamed = 0
                    for i,M in enumerate(MOP.search_result):
                        spin(' Slice-renaming... '+pprc.inc())
                        tag_string = ' '.join(getM2tags(M))
                        if cmds[0] in tag_string: # modifying
                            modified += 1
                            while cmds[0] in tag_string:
                                tag_string = tag_string.replace(cmds[0], cmds[1])
                                renamed += 1
                            M = setM2tags(M, set(tag_string.split()) )
                            M = MOP.save(M,i)
                    if renamed:
                        MOP.update_tags() # memorize
                        clrln(' [*] Replaced '+BRIGHT+str(renamed)+NORMAL+' occurrences in '+BRIGHT+str(modified)+NORMAL+' items.\n')
                    else:
                        clrln(' [!] No occurrence was found.\n')
                else:
                    cprint(' [i] Usage:', help.usage2(kw.renameMatchingGroup,' <substring> <replacement>')+'\n [i] Replaces all substring occurrences in tags.', markup=True)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.renameMatchingWhole:
                if len(cmds) > 1: # rename
                    total = pprc.reset(len(MOP.search_result))
                    modified = 0
                    renamed = 0
                    for i,M in enumerate(MOP.search_result):
                        spin(' Slice-renaming!... '+pprc.inc())
                        if any( cmds[0] in tag and cmds[1] != tag for tag in getM2tags(M) ): # modifying
                            modified += 1
                            tags = list(getM2tags(M))
                            for ti,tag in enumerate(tags):
                                if cmds[0] in tag and cmds[1] != tag:
                                    tags[ti] = cmds[1]
                                    renamed += 1
                            M = setM2tags(M, set(tags) )
                            M = MOP.save(M,i)
                    if renamed:
                        MOP.update_tags() # memorize
                        clrln(' [*] Replaced '+BRIGHT+str(renamed)+NORMAL+' occurrences in '+BRIGHT+str(modified)+NORMAL+' items.\n')
                    else:
                        clrln(' [!] No occurrence was found.\n')
                else:
                    cprint(' [i] Usage:', help.usage2(kw.renameMatchingWhole,' <substring> <replacement>')+'\n [i] Replaces all substring occurrences in tags.', markup=True)
                continue
            #1------------------------------------------------------------------
            if cmd in kw.intersection:
                itags = MOP.get_intersecting_tags()
                if itags:
                    xerox.copy(str(' '.join(itags)))
                    cprint(' [i] Copied '+BRIGHT+str(len(itags))+NORMAL+' intersecting tags to clipboard.')
                else:
                    cprint(' [i] No tag intersection found.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.difference:
                itags = MOP.get_unique_tags()
                if itags:
                    xerox.copy(str(' '.join(itags)))
                    cprint(' [i] Copied '+BRIGHT+str(len(itags))+NORMAL+' orphaned tags to clipboard.')
                else:
                    cprint(' [i] No tag difference found.')
                continue
            #1------------------------------------------------------------------
            if cmd in kw.rare:
                itags = MOP.get_rare_tags()
                if itags:
                    xerox.copy(str(' '.join(itags)))
                    cprint(' [i] Copied '+BRIGHT+str(len(itags))+NORMAL+' rare tags to clipboard.')
                else:
                    cprint(' [i] No rare tags found.')
                continue
            #1------------------------------------------------------------------
            # kw.sim
            if cmd in kw.cpl('similar pSimilar similarFuz pSimilarFuz'):
                reduce = True
                #clipb2img = False
                #clipboard_phash = None
                for i,c in enumerate(cmds):
                    if c.strip() in kw.reduceNot:
                        reduce = False
                        break
                    #if c.strip() in kw.clipb2img:
                    #    clipb2img = True
                    #    im = ImageGrab.grabclipboard()
                    #    im.save('c:\somefile.png','PNG')
                    #    try:
                    #        MOP.search_result = [genM2('c:\somefile.png', phash=imhash_im_object(im))]
                    #        print 'PHASH:', imhash_im_object(im), MOP.search_result[0]
                    #        #clipboard_phash = imhash_im_object(im)
                    #    except:
                    #        #clipboard_phash = 'error'
                    #        break

                #if clipboard_phash == 'error':
                #    cprint(' [!] No image found in clipboard.')
                #    continue

                cancel = False
                old_search_result = MOP.search_result[:]

                fuzz = cmd in kw.cpl('similarFuz pSimilarFuz')
                perceptual = cmd in kw.cpl('pSimilar pSimilarFuz')

                tagslist = list()
                if cmds: # parameters (tags) given:
                    filter_tags = list() if any(c in ('-','--') for c in cmds) else None
                    add = True # search for similar SELECTED (+) tags but filter out *RESULTS* having (-) tags:
                    tag_strength = 1
                    for c in cmds:
                        if c == '+':
                            add = True
                        elif c == '-':
                            add = False
                        elif c == '++':
                            tagslist += flatten_list(getM2tags(M) for M in old_search_result)
                            tag_strength = len(old_search_result)
                            add = True # add all the tags of selection
                        elif c == '--':
                            tagslist += flatten_list(getM2tags(M) for M in old_search_result)
                            add = False # add all the tags of selection
                        elif add is True:
                            #reduce = False # no reducing if (+) tags added as parameters
                            for x in xrange(tag_strength): # matters at count_sort()
                                tagslist.append(c)
                        elif add is False: # not add
                            filter_tags.append(c)
                else:
                    filter_tags = None

                if tagslist: # parameter (+) tags set:
                    MOP.search_result[:] = list()
                    #print tagslist
                else:
                    tagslist = flatten_list( getM2tags(M) for M in MOP.search_result )

                variantIds = [ MOP.hash_variants_by_hash(M.hash) for M in MOP.search_result if M.hash ] # [None, 'hash' / 'hash hash hash', ...]
                #variantIds = [ e if not e is None and ' ' in e else str(e) for e in variantIds ] # [ 'hash', 'hash hash hash', ... ]
                variantIds = [ e for e in variantIds if not e is None and ' ' in e ] # [ 'hash hash', 'hash hash hash', ... ]
                varSeq1 = tuple(count_sort(' '.join(variantIds).split()))#sorted(variantIds)# sorted kills selection preference order of selection

                if perceptual:
                    pHashes1 = [ M.phash for M in MOP.search_result if M.phash ]
                    uniqueSeq(pHashes1) # maybe not, if duplicates make notion stronger?? # seems ok (no difference)
                    #pHashes1 = count_sort(pHashes1) # wrong!
                    #pHashes1 = list() # perceptual ratio
                    #for M in MOP.search_result:
                    #    if M.phash:
                    #        #pHashes1.append(imhash(M.filepath))
                    #        pHashes1.append(M.phash)
                    #pHashes1.sort()
                    if not pHashes1:
                        cprint(' [!] Selected items have no perceptual data.')
                        if really(' Perform a standard search instead?', default=False):
                            perceptual = False
                        else:
                            continue

                if reduce and len(old_search_result) > 1:# and float(len(tagSeq1)) / known_tags_amt >= 0.00: # % of availible
                    # REDUCING TAG POOL IF TAGS/ALL_TAGS RATIO IS TO HIGH:
                    reduced = True
                    tagSeq1 = count_sort(tagslist) # sort tags by occurrence amt
                    selected_tags_amt = len(tagSeq1)
                    #known_tags_amt = len(uniqued(MOP.tags))
                    known_tags_amt = len(set(MOP.tags))
                    ratio = float(selected_tags_amt) / known_tags_amt
                    # REDUCING TAG AMOUNT IN SELECTION:
                    tagSeq1 = tagSeq1[:int(selected_tags_amt**(1-ratio**0.6))]#0.8 higher=more tags
                    #print tagSeq1
                    #if not buffer_mode:
                    tagSeq1.sort() # better matches since Ms have their tags sorted

                    if perceptual:
                        selected_phashes_amt = len(pHashes1)
                        #known_phashes_amt = sum(map(lambda m:not m.phash is None,MOP.search_result))
                        known_phashes_amt = sum(True for M in MOP.search_result if M.phash)
                        pratio = float(selected_phashes_amt) / known_phashes_amt
                        # REDUCING PHASHES AMT IN SELECTION:
                        pHashes1 = pHashes1[:int(selected_phashes_amt**(1-pratio**0.6))]#0.8 higher=more tags
                        #pHashes1.sort() # do not sort
                        if TECHNICAL_INFO:
                            cprint(' [i] Using reduced tag sequence ('+str(selected_tags_amt)+'->'+str(len(tagSeq1))+').')
                            cprint(' [i] Retain ratio is '+str(selected_tags_amt)+'/'+str(known_tags_amt)+'='+str(round(ratio,2))+'.')
                            if not buffer_mode:
                                cprint( definition(' [i] Reduced to:',' '.join(pHashes1),width=consoleX-2) )
                            cprint(' [i] Using reduced phash sequence ('+str(selected_phashes_amt)+'->'+str(len(pHashes1))+').')
                            cprint(' [i] Retain ratio is '+str(selected_phashes_amt)+'/'+str(known_phashes_amt)+'='+str(round(pratio,2))+'.')
                            if not buffer_mode:
                                cprint( definition(' [i] Reduced to:',' '.join(pHashes1),width=consoleX-2) )
                        elif not buffer_mode:
                            cprint(' [i] Using reduced tag & phash sequence.')
                        pHashes1 = tuple(pHashes1) # BAM!
                    elif TECHNICAL_INFO:
                        cprint(' [i] Using reduced tag sequence ('+str(selected_tags_amt)+'->'+str(len(tagSeq1))+').')
                        cprint(' [i] Retain ratio is '+str(selected_tags_amt)+'/'+str(known_tags_amt)+'='+str(round(ratio,2))+'.')
                        if not buffer_mode:
                            cprint( definition(' [i] Reduced to:',' '.join(tagSeq1),width=consoleX-2) )
                    elif not buffer_mode:
                        cprint(' [i] Using reduced tag sequence.')
                else:
                    reduced = False
                    tagSeq1 = sorted(set(tagslist)) # better matches since Ms have their tags sorted
                    #print tagSeq1
                tagSeq1 = tuple(tagSeq1) # BAM!

                #if fuzz: # string comparison # remove the "sorted" thing
                #    tagSeq1 = ' '.join(tagSeq1)

                MOP.search(sort=False)#SELECTION.select(MOP, verbose=False, sort=False) # hash, phash, name, tags should suffice

                ratio__M = list()
                total = pprc.reset(len(MOP.search_result))
                sm = SequenceMatcher()
                #sim_ratio = sm.quick_ratio
                sim_ratio = sm.ratio
                #print varSeq1
                for i,M in enumerate(MOP.search_result):
                    try:
                        spin(' Detecting similarities... '+pprc.inc())

                        # VARIANT SIMILARITY RATIO
                        #variantId = MOP.hash_variants_by_hash(M.hash) or M.hash if M.hash else '' # [None, 'hash' / 'hash hash hash', ...]
                        #vRatio = similar(variantId,varSeq1)
                        if M.hash:
                            sm.set_seqs((M.hash,),varSeq1); vRatio = sim_ratio()
                            #sm.set_seqs(M.hash,' '.join(varSeq1)); vRatio = sim_ratio()
                            #if M.hash in varSeq1: print M.hash,varSeq1,vRatio
                        else:
                            vRatio = 0#.0
                        # PERCEPTUAL SIMILARITY RATIO
                        if perceptual:
                            if pHashes1 and M.phash:
                                #pRatio = median( similar(pHash1,M.phash) for pHash1 in pHashes1 )
                                sm.set_seq2(M.phash)#; pRatio = median( sm.set_seq1(pHash1).ratio() for pHash1 in pHashes1 )
                                pRatio = list()
                                for pHash1 in pHashes1:
                                    sm.set_seq1(pHash1)
                                    pRatio.append(sim_ratio())
                                pRatio = median(pRatio)
                                #print pRatio
                            else:
                                pRatio = 0#.00 # filetype is different

                        # TAG SIMILARITY RATIO
                        #M.tags.discard(None)
                        #if fuzz:
                            #tagSeq2 = ' '.join(sorted(getM2tags(M)))
                        ##tagSeq2 = M.tags
                        #else:
                        #    #tagSeq2 = sorted(getM2tags(M))
                        #    tagSeq2 = split(M.tags)

                        #tRatio = similar(tagSeq1,tagSeq2.split())
                        sm.set_seqs(tagSeq1,M.tags.split()); tRatio = sim_ratio()
                        if perceptual: # calculate M.meta data ratio
                            mRatio = 1
                        #fRatio = similar(' '.join(tagSeq1),tagSeq2)
                        sm.set_seqs(' '.join(tagSeq1),M.tags); fRatio = sim_ratio()
                        if fuzz:
                            # FILENAME/URL SIMILARITY RATIO
                            sm.set_seqs(' '.join(M2.filepath for M2 in MOP.search_result),M.filepath); urlRatio = sim_ratio()
                        # OVERALL SIMILARITY RATIO
                        if perceptual: # also use M.meta data
                            simRatio = ((fRatio*1.5+urlRatio**-0.15+vRatio*1.5+tRatio*0.2+pRatio*4.5+mRatio*0.1)/7.8,M, (tRatio,pRatio,vRatio) ) if fuzz else ((tRatio*1.5+vRatio*1.5+fRatio*0.2+pRatio*4.5+mRatio*0.4)/7.6,M, (tRatio,pRatio,vRatio) )
                            #simRatio = ((fRatio*1.5+urlRatio**-0.15+vRatio*1.5+tRatio*0.2+pRatio*4.5)/7.7,M, (tRatio,pRatio,vRatio) ) if fuzz else ((tRatio*1.5+vRatio*1.5+fRatio*0.2+pRatio*4.5)/7.2,M, (tRatio,pRatio,vRatio) )
                        else:
                            #simRatio = ((fRatio*1.5+urlRatio**-0.15+vRatio*1.5+tRatio*0.2+mRatio*0.1)/3.8,M, (tRatio,None,vRatio) ) if fuzz else ((tRatio*1.5+vRatio*1.5+fRatio*0.2+mRatio*0.4)/3.6,M, (tRatio,None,vRatio) )
                            simRatio = ((fRatio*1.5+urlRatio**-0.15+vRatio*1.5+tRatio*0.2)/3.7,M, (tRatio,None,vRatio) ) if fuzz else ((tRatio*1.5+vRatio*1.5+fRatio*0.2)/3.2,M, (tRatio,None,vRatio) )
                        if simRatio[0]:
                            ratio__M.append(simRatio)
                    except KeyboardInterrupt:
                        if really(' Cancel?', default=True):
                            cancel = False
                            break

                if cancel:
                    MOP.search_result = old_search_result
                    continue

                if cmds and is_number(cmds[0]):
                    min_simRatio = abs(float(cmds[0]))%100.0
                    if min_simRatio > 1.0:
                        min_simRatio /= 100.0
                    reduce_to = len(ratio__M)
                else:
                    #min_simRatio = None
                    #reduce_to = int(sqrt(len(ratio__M))) * 2
                    reduce_to = len(ratio__M)
                    min_simRatio = median( e[0] for e in ratio__M ) ** 0.64

                MOP.search_result = list()

                if perceptual:
                    name = kw.pSimilarFuz[1] if fuzz else kw.pSimilar[1]
                else:
                    name = kw.similarFuz[1] if fuzz else kw.similar[1]

                ratio__M.sort(reverse=True)
                for i in xrange(reduce_to):
                    if ratio__M[i][0] >= min_simRatio:
                        if filter_tags and any(t==x for x in filter_tags for t in ratio__M[i][1].tags.split()):
                            #print ratio__M[i][1].hash
                            continue # skip items with unwanted (-) tags
                        MOP.search_result.append(ratio__M[i][1])
                clrln()
                if MOP.search_result and MOP.search_result != old_search_result:
                    reduced_ = 'reduced ' if reduced else ''
                    if len(MOP.search_result) > 2:
                        total = pprc.reset(len(MOP.search_result))
                        average = [r_p_m[0] for r_p_m in ratio__M[1:total]]
                        med = median(average)
                        average = sum(average)/(total-1)
                        if len(old_search_result) > 1:
                            amount_rating = med * int(sqrt(len(MOP.search_result))) * 2 / len(old_search_result)
                            if amount_rating < 0.0:
                                amount_rating = 0.0
                            if TECHNICAL_INFO and not buffer_mode:cprint(' [i] Similarity ratio ('+reduced_+BRIGHT+name[1:]+NORMAL+'): '+str(round(ratio__M[1][0],2))+' - '+str(round(ratio__M[total-1][0],2))+' ~ '+BRIGHT+str(round(med,2))+NORMAL+', overall: '+btint(str(round(amount_rating,2))))
                        else:
                            if TECHNICAL_INFO and not buffer_mode:cprint(' [i] Similarity ratio ('+reduced_+BRIGHT+name[1:]+NORMAL+'): '+str(round(ratio__M[1][0],2))+' - '+str(round(ratio__M[total-1][0],2))+' ~ '+btint(str(round(med,2))))
                    else:
                        if TECHNICAL_INFO and not buffer_mode:cprint(' [i] Similarity ratio ('+reduced_+BRIGHT+name[1:]+NORMAL+'): '+str(round(ratio__M[1][0],2)))
                    if addMode: MOP.search_result = MOP.filter_duplicate_metadata(MOP.search_result+previous_search)
                    #if not buffer_mode and not technical_info:cprint(' [*] Similar items found.')
                    if tag_msg:
                        for rule in tag_msg:
                            msg_on_tag_matches = MOP.msg_on_tag(rule)
                else:
                    if not buffer_mode and really(' Nothing similar found. Cancel?', default=True):
                        MOP.search_result = old_search_result[:]
                continue

            #1------------------------------------------------------------------
            #path = os.path.normcase(os.path.normpath(raw[len(cmd):].strip())) # removes '-flag' from raw
            path = raw[len(cmd):].strip() # removes '-flag' from raw
            #1------------------------------------------------------------------
            if   cmd in ('-copy','-copy-follow', '-t','-p'): f_op_algo = shutil.copy2#shutil.copyfile
            elif cmd in kw.move: f_op_algo = shutil.move
            else: f_op_algo = None

            if cmd == '-t':
                try:
                    shutil.rmtree(temporary_directory)
                except: pass#print_exception()

            if f_op_algo: # copy or move operations
                if path:
                    if path == '.':
                        path = ''
                    elif path[-1] != os.sep: # adding os separator to path2 (ONLY FOLDERS ALLOWED!)
                        path += os.sep
                    #path = path.replace(':', os.path.sep)
                    path2_n = format_path(path)
                    if path2_n[-1] != os.sep: # adding os separator to path2 (ONLY FOLDERS ALLOWED!)
                        path2_n += os.sep
                    if not os.path.exists(path2_n):
                        try:
                            os.makedirs(path2_n)
                        except:
                            print_exception()
                            continue
                elif not cmd in kw.move:
                    path2_n = format_path(temporary_directory[:])
                    if path2_n[-1] != os.sep: # adding os separator to path2 (ONLY FOLDERS ALLOWED!)
                        path2_n += os.sep
                    if not os.path.exists(path2_n):
                        try:
                            os.makedirs(path2_n)
                        except:
                            print_exception()
                            continue
                else:
                    cprint(' [!] Moving files to temporary directory is forbidden. Try copying instead.')
                    continue
                path2_na = os.path.realpath(path2_n) + os.sep # normalised & absolute
                if not os.path.exists(path2_na):
                    try:
                        os.makedirs(path2_na)
                    except:
                        print_exception()
                        continue
                pprc.reset(len(MOP.search_result))
                operation = ('Moving' if cmd in kw.move else 'Copying') + ' files... '
                for i,M in enumerate(MOP.search_result):
                    if not os.path.exists(M.filepath):
                        clrln()
                        cprint(' [!] File is not on disk:')
                        MOP.show_info(M); print ''
                        pprc.inc()
                        continue
                    if M2is_remote(M):
                        pprc.inc()
                        continue # skip remote paths

                    spin(operation+M.hash+' '+pprc.inc())
                    path1_n = link_to_path(M.filepath) # normalised
                    path1_na = os.path.realpath(path1_n) # normalised & absolute

                    filename = ntpath.basename(path1_na)

                    # UPDATING PATH2 INDIVIDUALLY WITH EXTRA FOLDERS
                    path2_nE = path2_n[:]
                    path2_naE = path2_na[:]
                    extra_folders = ''
                    for tag in getM2tags(M):
                        if tag.startswith(extra_folder_tag+':') and tag.partition(extra_folder_tag+':')[2].strip():
                            extra_folders += tag.partition(extra_folder_tag+':')[2].replace(':',os.sep).replace('?',' ').replace('"','').strip()+os.sep
                    if extra_folders:
                        if not path2_n.endswith(extra_folders):
                            path2_nE = os.path.join(path2_n, extra_folders)
                            path2_naE = os.path.join(path2_na, extra_folders)
                        if not os.path.exists(path2_naE):
                            try:
                                os.makedirs(path2_naE)
                            except:
                                print_exception()
                                continue

                    if path1_na == path2_naE+filename: # destination is source, just rename
                        if path1_n == path2_nE+filename: # exact match (as in: "a.txt a.txt" or "-copy a.txt .\a.txt")
                            continue
                        M = setM2filepath(M, path2_nE+filename)
                        #MOP.search_result[i] = MOP.save(M)
                        MOP.save(M,i)
                        continue

                    # COPY / MOVE TO AVALIBLE DESTINATION (but still, avoid overwriting by renaming)

                    n, _ = 0, '' # 'o.O'
                    name, ext = os.path.splitext(filename)

                    done = False
                    while os.path.exists(path2_naE+name+_+ext): # filepath collision
                        #if log: print '\n [!] COLLISION: '+path2_naE+name+_+ext
                        if n > 9999:
                            done = True
                            break
                        if hashfile(path2_naE+name+_+ext) != M.hash: # different data
                            _ = '_'+str(i)
                            n += 1
                        else: # exact data is in destiny so remove file from source
                            if cmd in kw.cpl('move copyFollow'):
                                M = setM2filepath(M, path2_nE+name+_+ext)
                                #MOP.search_result[i] = MOP.save(M)
                                MOP.save(M,i)
                            if cmd in kw.move:
                                try:
                                    send2trash(path1_na)#os.remove(path1_na)
                                except:
                                    clrln()
                                    cprint(' [!] Could not delete: '+path1_na)
                            done = True
                            break
                    if done:
                        continue
                    if _ == '': # use NEW FILENAME! (copy/move)
                        filename = name+_+ext
                    try:
                        f_op_algo(path1_na, path2_naE+filename) # https://stackoverflow.com/questions/123198/how-do-i-copy-a-file-in-python
                        if cmd in kw.cpl('move copyFollow'):
                            M = setM2filepath(M,path2_nE+filename)
                            #MOP.search_result[i] = MOP.save(M)
                            MOP.save(M,i)
                    except:# IOError as e:
                        cprint( ' [!] copy/move/rename error:\n' )
                        print (path1_na, ' -> ',  path2_naE+filename)
                        continue
                #self.update_tags() # update database snapshot (new tags need an update)
                #if not buffer_mode:
                #    if cmd in kw.move:
                #        clrln(' [*] Moved\n')
                #    elif cmd in kw.cpl('copy copyFollow'):
                #        clrln(' [*] Copied\n')
                if cmd in ('-t', ):
                    subprocess.call(system_cmd_for_directory_preview+[temporary_directory], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    if cmd == '-t':
                        clrln(' Removing temporary files...')
                        try:
                            shutil.rmtree(temporary_directory)
                        except:
                            clrln()
                            cprint(' [!] Cannot remove temporary files in: '+temporary_directory)
                        clrln()
                    continue
            #1------------------------------------------------------------------
            elif cmd in kw.cpl('fix lost present'):
                # CHECK FOR MISSING FILES IN SELECTION
                missing_files = list()
                pprc.reset(len(MOP.search_result))
                for i,M in enumerate(MOP.search_result):
                    spin(' Verifying selected files... '+pprc.inc()+' '+M.hash)
                    if M2file_is_missing(M):
                        missing_files.append(M)
                clrln()
                if not missing_files:
                    cprint(' [i] All '+BRIGHT+MOP.total()+NORMAL+' selected files are in place.')
                    # ALL OPERATIONS INVOLVING LOST FILES ARE FUTILE, THEREFORE...
                    continue
                #2--------------------------------------------------------------
                if cmd in kw.lost:
                    if len(missing_files)<50 or really(' Display info for '+str(len(missing_files))+' files?'):
                        for i,M in enumerate(missing_files):
                            MOP.show_info(M, str(i+1))
                        print ''
                    cprint(' [i] Type "(**-fix**|**-find**) <dir/to/search>" to search for the '+ error_btint(str(len(missing_files)))+ ' missing file(s).', markup=True)
                    MOP.search_result = missing_files; total = len(MOP.search_result)
                    continue
                #2--------------------------------------------------------------
                if cmd in kw.present and missing_files:
                    MOP.search_result = sorted(list(set(MOP.search_result).difference(missing_files)))
                    total = len(MOP.search_result)
                    continue
                #2--------------------------------------------------------------
                # ELSE: ASSUME THE OPERATION IS kw.fix or kw.find
                path = path.strip('"') # ????????? earlier? maybe on input?
                cprint(' [i] Searching for ' + str(len(missing_files)) + ' missing files.')# in:\n ' + BRIGHT+path+NORMAL)
                filepath_index = [ spin(suffix=' Generating file-index...', embed=(dirpath, f)) for dirpath, dirnames, files in os.walk(path) for f in files ]

                #if cmd in kw.fixByName:
                #    total = len(missing_files); i = 0
                #    spin(' Searching for matching filenames... '+str(percent(i,total))+'%')
                #    continue

                #filepath_index = [ (dirpath, f) for dirpath, dirnames, files in os.walk(path) for f in files ]
                filepath_index = [ os.path.join(dirpath,f) for dirpath,f in filepath_index ]
                #print filepath_index
                clrln(' [i] ' + BRIGHT+str(len(filepath_index))+NORMAL + ' files to scan.\n')
                total = pprc.reset(len(filepath_index))
                hash_index = [ spin(' Generating hashes... '+pprc.inc(), embed=hashfile(fp)) for i,fp in enumerate(filepath_index) ]
                failed_matches = list()
                total = len(missing_files); i = 0
                for x,M in enumerate(missing_files):
                    spin(' Searching for matching file signatures...'+(' ('+str(i)+'/'+str(total)+', '+str(percent(i,total))+'% found)')*bool(i))
                    try:
                        pos = hash_index.index(M.hash)
                    except:
                        pos = None
                    if not pos is None:
                        #clrln(M.hash +' : '+ M.filepath +' = '+ filepath_index[pos])
                        M = setM2filepath(M,filepath_index[pos])
                        M = MOP.save(M)
                        missing_files[x] = M # update selection
                        del hash_index[pos]
                        del filepath_index[pos]
                        if not buffer_mode:
                            #clrln(' [*] Found: '+M.filepath+'\n')
                            clrln()
                            cprint(' [+] '+M.hash+' found: '+M.filepath)
                        i += 1
                    else:
                        if M.hash:
                            clrln()
                            cprint(' [-] '+M.hash+' not found.')
                        elif M.filepath:
                            clrln()
                            cprint(' [i] Skipping: '+M.filepath)
                        failed_matches.append(M)
                MOP.update_tags()
                if failed_matches:
                    MOP.search_result = failed_matches # update MetadataOperator search results with te list of missing files
                    total = len(MOP.search_result)
                    #clrln(' [i] Type again "-fix another/dir" to search for the '+BRIGHT+str(total)+NORMAL+' missing file(s).\n')
                    clrln()
                    cprint(' [i] Type "(**-fix**|**-find**) <dir/to/search>" to search for the '+ error_btint(str(total))+ ' missing file(s).', markup=True)
                else:
                    MOP.search_result = missing_files # a single file
                    if i==1:
                        #MOP.search_result = missing_files # a single file
                        clrln(' [i] Found it.\n')
                    else:
                        clrln(' [i] All '+btint(str(i))+' files were found.\n')
                #2--------------------------------------------------------------
            #1------------------------------------------------------------------
            elif cmd in kw.detach:
                if not really(' Remove url\'s from selected items? Really?'):
                    cprint(' [*] Skipped')
                    continue
                for i,M in enumerate(MOP.search_result):
                    spin(prefix=' Detaching files'+'.'*((100-percent(i,total))/(consoleX/16))+'.', suffix='.'*(percent(i,total)/(consoleX/16)))
                    if cmds and cmds[0] and M.filepath and not M2is_remote(M):
                        M = setM2filepath(M, os.path.join(expandvars_nfr_only(cmds[0]),os.path.basename(M.filepath)) )
                    else:
                        M = setM2filepath(M, '')
                    #M = MOP.save(M)
                    MOP.save(M,i)
                MOP.update_tags() # really?
            continue
            #1------------------------------------------------------------------
        if MOP.db:
            #1----------------------------------------------------------------------
            # IF ALL ELSE FAILS: ASSUME raw IS A TAG-SEARCH/SELECTION COMMAND
            #cprint(raw)
            #cprint(debug_tag_input(raw))
            #print raw
            raw = debug_tag_input(raw).split()
            #print raw
            #cprint('[*] TAG SEARCH')
            if use_aliases:
                raw = unalias_list(raw)
            #raw = filter(None,raw.split()) # convert multiple spaces to single
            # FIX: DOUBLE CHEKING FOR ALIASES!!!
            alias_detected = False
            if raw[0] in kw.subselect:

                if len(raw) > 1:
                    s = ' '.join(raw) # for time parsing purposes
                    
                    m_added = re.search(r'(^|\s)(added)([><]{0,1})\[(.*?)\]', s)
                    if m_added:
                        #MOP.search_result = filter(None, MOP.search_result)
                        MOP.search_result = filter(lambda x:x.added, MOP.search_result)
                        added_sign = m_added.group(3)
                        try:
                            select_added = maya.when(m_added.group(4))
                        except:
                            cprint(' [!] Sorry didn\'t understand *when*.')
                            continue
                        s = re.sub(r'(^|\s)(added)([><]{0,1})\[(.*?)\]',r'\g<1>',s)
                        if not added_sign:
                            MOP.search_result = filter(lambda x:maya.parse(str(x.added)).slang_date()==select_added.slang_date(), MOP.search_result)
                        elif added_sign=='>': # older than
                            MOP.search_result = filter(lambda x:x.added<select_added.datetime(naive=True), MOP.search_result)
                        elif added_sign=='<': # younger than
                            MOP.search_result = filter(lambda x:x.added>select_added.datetime(naive=True), MOP.search_result)

                    m_modified = re.search(r'(^|\s)(modified)([><]{0,1})\[(.*?)\]', s)
                    if m_modified:
                        #MOP.search_result = filter(None, MOP.search_result)
                        MOP.search_result = filter(lambda x:x.modified, MOP.search_result)
                        modified_sign = m_modified.group(3)
                        try:
                            select_modified = maya.when(m_modified.group(4))
                        except:
                            cprint(' [!] Sorry didn\'t understand *when*.')
                            continue
                        s = re.sub(r'(^|\s)(modified)([><]{0,1})\[(.*?)\]',r'\g<1>',s)
                        if not modified_sign:
                            MOP.search_result = filter(lambda x:maya.parse(str(x.modified)).slang_date()==select_modified.slang_date(), MOP.search_result)
                        elif modified_sign=='>': # older than
                            MOP.search_result = filter(lambda x:x.modified<select_modified.datetime(naive=True), MOP.search_result)
                        elif modified_sign=='<': # younger than
                            MOP.search_result = filter(lambda x:x.modified>select_modified.datetime(naive=True), MOP.search_result)

                    raw = s.split() # reverting after time parsing is done

                    #if not raw[1] in MOP.tags: # slice selection:    
                    if len(raw) > 1 and is_slice(raw[1]): # slice selection:
                        sub_selection = slice_select(MOP.search_result, ' '.join(raw[1:]))
                        count = len(sub_selection)
                        #MOP.search_result = MOP.filter_duplicate_metadata(sub_selection)
                        MOP.search_result = sub_selection
                        total = len(MOP.search_result)
                        if not buffer_mode and count > total:
                            cprint(' [i] Some overlapping items were truncated.')
                        if total and tag_msg:
                            for rule in tag_msg:
                                msg_on_tag_matches = MOP.msg_on_tag(rule)
                                #print len(msg_on_tag_matches)
                        continue
                else:
                    cprint(' [i] Please, specify some tags to search for in the sub-selection.')
                    continue
                select_from_selection = True
                raw = ' '.join(raw[1:])
            else:
                select_from_selection = False
                raw = ' '.join(raw)

            # 1. EXPAND ALIASES IF ANY:
            if set(MOP.aliases).intersection(raw.split()): # alias detected
                alias_detected = True
                cmds = filter(None,raw.strip().split())
                for i,cmd in enumerate(cmds):
                    if cmd in MOP.aliases:
                        match = MOP.alias_db.select(alias=unicode(cmd))
                        if match:
                            cmds[i] = match[0].selection
                            if ' | ' in cmds[i]:
                                cmds[i] = ' | ' + cmds[i] + ' | ' # miessing-up raw with "|" (ORs)
                raw = ' '.join(cmds)
                if ' | ' in raw: # cleaning-up the "|" (ORs) overkill in raw
                    raw = ' | '.join(filter(None,raw.split(' | ')))
            # 2. DO BULK TAG-SEARCH:
            if ' | ' in raw: # "if" because aliases don't have to contain _ORs
                if ' * ' in raw:
                    _AND = ' '.join(raw.split(' * ')[1:]) # debug for multiple asterisks
                    raw = raw.split(' * ')[0]
                else:
                    _AND = ''
                _ORs = filter(None,raw.split(' | '))
                _ORs = map(lambda x:x.strip(),_ORs)
                selections = list()
                for i,_OR in enumerate(_ORs):
                    _ORs[i] = _OR = ' '.join((_OR, _AND))
                    inc,exc,tin,tex,sinc,sexc = parse_inclusions(_OR, MOP, use_wordnet)
                    operations = flatten_list(filter(None,[inc,exc,tin,tex,sinc,sexc]))
                    if not any(operations):
                        if skippy and not buffer_mode:
                            cprint(' [i] Search aborted.')
                        continue
                    selections.append(Selection(inc,exc,tin,tex,sinc,sexc))
                raw = ' | '.join(_ORs)
                #if not cmd_ln_mode or not buffer_mode:
                #    print ' [i] Request: '+raw
                buffer_mode = True
                MOP.search_result = BulkOperation(selections).run(MOP, verbose=False, over_selection=select_from_selection)
                if addMode: MOP.search_result = MOP.search_result+previous_search
                MOP.search_result = MOP.filter_duplicate_metadata()
                total = len(MOP.search_result)
                #if total: print '1a',tag_msg
                if total and tag_msg:
                    #cprint('2a!!!!!!!!!!!!!!!!!!!')
                    for rule in tag_msg:
                        msg_on_tag_matches = MOP.msg_on_tag(rule)
                        #print len(msg_on_tag_matches)
            # 3. OR ORDINARY TAG-SEARCH:
            else:
                inc,exc,tin,tex,sinc,sexc = parse_inclusions(debug_tag_input(raw), MOP, use_wordnet)
                operations = flatten_list(filter(None,[inc,exc,tin,tex,sinc,sexc]))
                if not any(operations):
                    if skippy and not buffer_mode:
                        cprint(' [i] Search aborted.')
                    #if first_run:
                    #    cprint(definition(' [i]','You tried to search for some tags but got no results. Maybe such tags do not exist or not a single item has all of them.'))
                    continue
                buffer_mode = True # won't disply index timing
                Selection(inc,exc,tin,tex,sinc,sexc).select(MOP, verbose=False, from_selection=select_from_selection)#MOP.search(raw)
                if addMode: MOP.search_result = MOP.filter_duplicate_metadata(MOP.search_result+previous_search)
                total = len(MOP.search_result)
                if total and tag_msg:
                    for rule in tag_msg:
                        msg_on_tag_matches = MOP.msg_on_tag(rule)
                        #print len(msg_on_tag_matches)
            if alias_detected:
                cprint(definition(' [i] Expands to:', str(raw)))



    clrln(' Unloading...')
    MOP.set_database() # None, cleanup & close
    DBA_NAME = ''
    try:
        shutil.rmtree(temporary_directory)
    except: pass#print_exception()
    try:
        os.remove(os.path.join(HOME_DIR,'nfr_collage.jpg'))
    except: pass
    try:
        os.remove(os.path.join(SCRIPT_DIR,'.raw'))
    except: pass
    try:
        os.remove(os.path.join(HOME_DIR,'nfr_clipboard_image.png'))
    except: pass
    os.chdir(OLD_WORKING_DIR) # set old working dir on program close
    clrln() # clear "unloading..." indicator

if DEBUG_PERFORMANCE:
    pr.disable()
    s = StringIO.StringIO()
    sortby = 'cumulative'
    ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    ps.print_stats()
    print s.getvalue()
