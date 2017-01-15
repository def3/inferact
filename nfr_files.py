#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

# def space_out_similar_prefix(src, to_space_out):
    # spaced = src.split(os.path.sep)
    # source = src.split(os.path.sep)
    # i = 0
    # while i<len(spaced)-1:
        # if source[i]==spaced[i]:
            # spaced[i]=' '*(len(spaced[i]))
        # i+=1
    # return ' '.join(spaced)

def format_path_nt(filepath):
    #filepath = os.path.normpath(os.path.normcase(filepath)).strip('"').strip("'")
    #filepath = expandvars_nfr(filepath)
    return os.path.normpath(os.path.normcase(filepath)).strip('"').strip("'") # fixes slashes & quotation marks. returns not OS poratble path!
    #return filepath.replace('\\', '/') # for Windows to Unix compatibility (works on relative paths only)
    #return os.path.normpath(os.path.normcase(filepath)).replace('\\', '/').strip('"').strip("'")
def path_nt2unix(path):
    return os.path.normpath(path.replace('\\', '/')) # for Windows to Unix compatibility (works on relative paths only)
def format_path_unix(filepath):
    return os.path.normpath(filepath)
format_path = format_path_nt if os.name == 'nt' else format_path_unix

def get_subpath(filepath):
    if os.path.isfile(filepath):
        return os.sep.join(os.path.split(filepath)[:-1])
    return filepath

def is_samepath(path1, path2): # does path1 point ot the same dst as path2?
    #path1n = os.path.normpath(os.path.normcase(path1))
    path1n = os.path.normpath(path1)
    #path2n = os.path.normpath(os.path.normcase(path2))
    path2n = os.path.normpath(path2)
    #print(path1n+'\n'+path2n)
    if path1n == path2n:
        return True
    if os.path.realpath(path1n) == os.path.realpath(path2n):
        return True
    return False

def is_subdir(path1, path2): # is path1 a sub-dir of path2?
    path1n = os.path.realpath(os.path.normpath(path1))
    path2n = os.path.realpath(os.path.normpath(path2))
    return path1n.startswith(path2n)

def filter_subdirs(paths):
    paths_ = paths[:]
    for i,path in enumerate(paths_):
        if path is None:
            continue
        for i2,path2 in enumerate(paths_):
            if i == i2 or path2 is None:
                continue
            if is_subdir(path2, path):
                paths_[i2] = None
    paths_ = filter(None,paths_)
    return paths_

def is_path_variation(path1, path2): # means the same but differs in expression
    return path1 != path2 and is_samepath(path1, path2)

from hashlib import sha1 as default_algo # https://docs.python.org/2/library/hashlib.html
default_algo_length = len(default_algo().hexdigest())


errlog_filepath = 'errlog.txt'
def errlog(element, rewrite=False, filepath=None):
    mode = 'w' if rewrite else 'a'
    if filepath is None:
        global errlog_filepath
        filepath = errlog_filepath
    try:
        with open(filepath, mode) as f:
            for e in element:
                f.write(str(e),)
            f.write('\n')
    except:
        print(' [!] Error writing debug info to errlog.txt!')
err = errlog

try:
    import mp3hash # hashing for tagged music files (mp3, other?)
    def hashfile0(filepath, algo=default_algo): # https://stackoverflow.com/questions/1869885/calculating-sha1-of-a-file
        try:
            if mp3hash.TaggedFile(open(filepath,'rb')).has_id3v2: # alters the handle data in-place!
                #print('tagged-id3v2 found & hashing... '+filepath)
                return mp3hash.mp3hash(filepath, hasher=algo())#+'-mp3hash'
            algo = algo()
            algo.update(open(filepath,'rb').read())
            return algo.hexdigest()
        except:# IOError as e:
            return None
    using_mp3hash = True
    def hashfile1(filepath, algo=default_algo): # https://stackoverflow.com/questions/1869885/calculating-sha1-of-a-file
        try:
            with open(filepath,'rb') as f:
                if mp3hash.TaggedFile(f).has_id3v2:
                    #print('tagged-id3v2 found & hashing... '+filepath)
                    return mp3hash.mp3hash(filepath, hasher=algo())#+'-mp3hash'
                algo = algo()
                algo.update(f.read())
        except:# IOError as e:
            return None
        return algo.hexdigest()
    using_mp3hash = True
except:
    def hashfile0(filepath, algo=default_algo): # https://stackoverflow.com/questions/1869885/calculating-sha1-of-a-file
        try:
            algo = algo()
            algo.update(open(filepath,'rb').read())
            return algo.hexdigest()
        except:# IOError as e:
            return None
    using_mp3hash = False

hashfile = hashfile0 # *testing* hash algo speed

def search_path_for_hash(path, hash): # http://stackoverflow.com/a/14798263
    #path = format_path(path) # WINDOWS
    filelist = [os.path.join(dirpath, f)
        for dirpath, dirnames, files in os.walk(path)
        for f in files if hashfile(os.path.join(dirpath, f))==hash]
    return filelist

def X_githash(data):
    algo = default_algo
    algo.update('blob %u\0' % len(data))
    algo.update(data)
    return algo.hexdigest()

def link_to_path_nt(path):
    #if os.path.islink(path): # is a symbolic link
    #    path = os.readlink(path)
    path = format_path(path)
    path = os.path.realpath(path)
    return path
def link_to_path_unix(path):
    #if os.path.islink(path): # is a symbolic link
    #    path = os.readlink(path)
    path = format_path_unix(path)
    path = os.path.realpath(path)
    return path
link_to_path = link_to_path_nt if os.name == 'nt' else link_to_path_unix

def is_exe(fpath): # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    return os.path.isfile(fpath) and os.access(fpath, os.X_OK)
def which(program): # https://stackoverflow.com/questions/377017/test-if-executable-exists-in-python/377028#377028
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

from send2trash import send2trash

def remove_duplicate_files(dir_with_unwanted_ext, undo=True):
    if len(dir_with_unwanted_ext) == 1:
        dir, skip_files_ending_with = dir_with_unwanted_ext[0], None
    else:
        dir, skip_files_ending_with = dir_with_unwanted_ext[0], dir_with_unwanted_ext[1].split()
        skip_files_ending_with = tuple(filter(None, skip_files_ending_with))
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
        preserved = []
        unique_hashes = []
        total = len(fh)
        for i,(f,h) in enumerate(fh):
            #spinner.animate(' Removing duplicates... '+str(percent(i,total))+'%')
            if h is None:
                try: send2trash(f)
                except: pass
            elif h not in unique_hashes:
                unique_hashes.append(h)
                preserved.append(f)
            else:
                if undo:
                    try: send2trash(f)
                    except: pass
                else:
                    try: os.remove(f)
                    except: pass
        #clrln()
        return (len(preserved), total)
    else: return (0, 0)

def filetype(filepath):
    ext = os.path.splitext(filepath)[-1].lower()
    if ext in ('.png', '.jpg', '.jpeg', '.gif'): return 'image'
    if ext in ('.wav', '.ogg', '.mp3', '.wma'): return 'audio'
    if ext in ('.avi', '.mp4', '.wmv', '.mpg', '.mpeg', '.webm'): return 'video'
    return 'other'

from PIL import Image
def datainfo(filepath):
    try:
        size = os.path.getsize(filepath)
        data = {'size': size}
    except:
        return None
    #data['location'] = os.path.dirname(os.path.abspath(filepath)) # os.path.realpath
    #data['filename'] = os.path.basename(os.path.abspath(filepath))
    data['type'] = filetype(filepath)
    if data['type'] == 'image':
        # image -> dimensions, mode, format, description, compression_ratio
        try:
            im = Image.open(filepath)
            data['dimensions'] = im.size
            data['mode'] = im.mode
            data['format'] = im.format
            if im.info.has_key('description'): data['description'] = im.info['description']
        except IOError:
            data['type'] = 'other'
    if data['type'] in ('video',):
        # video -> audible, duration, dimensions, video
        pass
    return data

def hashOrId(url):
    path = os.path.realpath(url) # try
    if os.path.isfile(path):
        if os.path.exists(path):
            return 'hash:'+hashfile(path)# local file
        return None # local file missing
    return 'id:'+url # link or text (determined by protocol type)
