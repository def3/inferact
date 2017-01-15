#!/usr/bin/python
# -*- coding: utf-8 -*-

part  = lambda s,sep=' ':s.partition(sep)[::2]
part1 = lambda s,sep=' ':s.partition(sep)[0]
part2 = lambda s,sep=' ':s.partition(sep)[2]
rpart  = lambda s,sep=' ':s.rpartition(sep)[::2]
rpart1 = lambda s,sep=' ':s.rpartition(sep)[0]
rpart2 = lambda s,sep=' ':s.rpartition(sep)[2]

def flags2dict(cmdln, flags, default=''):
    d = dict()
    current_flag = default
    for word in cmdln.split():
        if word in flags:
            current_flag = word
        if not d.has_key(current_flag):
            d[current_flag] = list()
        else:
            d[current_flag].append(word)
    return d

def get_flagged(cmdln, flags, flagged, default=''):
    d = flags2dict(cmdln, flags, default)
    try:
        if len(flagged) > 1:
            return flatten_list( [d[flag] for flag in flagged] )
        else:
            return d[flagged[0]]
    except:
        return None

def startswith_any(seq, seq2):
    for e in seq2:
        if seq.startswith(e):
            return e

def multipartition(seq, *seps):
    pos = len(seq)
    for s in seps:
        spos = seq.find(s)
        if -1 < spos < pos:
            pos = spos
            sep = s
    try:
        return seq.partition(sep)
    except:
        return seq, '', ''

def rmultipartition(seq, *seps):
    pos = -1
    for s in seps:
        spos = seq.rfind(s)
        if spos > pos:
            pos = spos
            sep = s
    try:
        return seq.partition(sep)
    except:
        return seq, '', ''

import itertools

def percent(amount, total):
    return int((amount+1) / float(total) * 100)
def percent_str(amount, total):
    if amount==total: return '100'
    ret = str(int((amount+1) / float(total) * 100))
    if ret=='100' and amount<total:
        return '99'
    else:
        return ret

class CrudeProgress(object):
    def __init__(self, total=100, index=0, custom=False, width=10):
        self.index = None
        self.total = None
        self.custom = None
        self.width = None
        self.set(total, index, custom, width)
    def set(self, total=None, index=None, custom=None, width=None):
        if total is not None:
            self.total = total
        if index is not None:
            self.index = index
        if custom is not None:
            #custom = False if custom is None else custom
            self.custom = custom if custom is False or len(custom)==4 else None
        if width is not None:
            self.width = width
        if custom:
            self.custom = tuple( e if e is not None else '' for e in custom )
            if not self.width:
                self.width = 10
            self.width = width-len(self.custom[0])-len(self.custom[3])
    def reset(self, total=None, index=None):
        if total is not None:
            self.total = total
        self.index = 0 if index is None else index
        if total is not None and index is not None:
            return (total, index)
        elif total is not None:
            return total
        elif index is not None:
            return index
    def inc(self, amount=1):
        self.index += amount
        if self.custom:
            blocks = int(self.index / float(self.total) * (self.width+1))
            return self.custom[0]+self.custom[1]*blocks+self.custom[2]*(self.width-blocks)+self.custom[3]
        else:
            return str(percent(self.index,self.total))+'%'

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def is_slice(text):
    if ':' in text:
        #return all(map(lambda x: x=='' or is_number(x), text.split(':',1))) or is_number(text)
        return all([ x=='' or is_number(x) for x in text.split(':',1) ])
    else:
        return text=='' or is_number(text)

def slice_select(seq, slices=':'):
    selection = list()
    slices = filter(is_slice,slices.split())
    for s in slices:
        if ':' in s:
            #a, b = map(str2int, s.rsplit(':', 1))
            (a, b) = s.rsplit(':', 1)
            a = str2int(a)-1 if a else None
            b = str2int(b)-1 if b else None
        else:
            b = str2int(s)
            a = b - 1
        selection += seq[a:b]
    return selection

def uniqued(seq):
    s = seq[:]
    uniques = list()
    while s:
        e = s.pop(0)
        if not e in uniques:
            uniques.append(e)
    return uniques
def uniquedTruthy(seq):
    s = seq[:]
    for i,e in enumerate(s): # filter duplicates retaining order
        if e in s[:i]:
            s[i] = None # duplicates => None
    return filter(None, s)
def uniqueSeq(seq): # in-place!
    uniques = len(set(seq))
    while len(seq) != uniques:
        for i,e in enumerate(seq): # filter duplicates retaining order
            if e in seq[:i]:
                del seq[i]
def uniqueTruthy(seq): # in-place!
    uniques = len(set(seq))
    while len(seq) != uniques:
        for i,e in enumerate(seq): # filter duplicates retaining order
            if not e or e in seq[:i]:
                del seq[i]

def count_uniques(seq):
    uniques = set(seq)
    result = []
    for unique in uniques:
        result.append((unique, seq.count(unique)))
    return result

def sorted_unique(seq, reverse=False):
    return sorted(set(seq), reverse=reverse)
def sorted_unique_amount(seq, reverse=False):
    unique = [ (unique, seq.count(unique)) for unique in set(seq) ]
    unique.sort(reverse=reverse)
    return unique

def str2int(s):
    try:
        return int(s)
    except ValueError:
        return 0
        
def really(question, default=False, get_input=False, y=None, n=None):
    output = None
    if default:
        answer = raw_input(question+' [yes] ').lower()
        if answer not in ('a', 'abort', 'cancel', 'none'):
            output = not answer in ('n','no')
    else:
        answer = raw_input(question+' [no] ').lower()
        if answer not in ('a', 'abort', 'cancel', 'none'):
            output = answer in ('y','yes')
    if get_input:
        output = output, answer
    if n and output is False:
        print(n)
    if y and output is True:
        print(y)
    return output

def debug_tag_input(raw, folder_autotagging=False):
    if folder_autotagging:
        # A:1/2/3 <-> A=1;2;3
        if '``' in raw:
            #if raw.startswith('``'):
            #    raw = raw[2:].replace(' ','_')
            #else:
            raw = part1(raw,'``')+part2(raw,'``').replace(' ','_')
            #raw = ' '.join(raw)
        raw = raw.replace('=',':').replace(';','/').replace('`','') # for directory autotagging
        #raw = ' '.join( tag.replace(';','/') if '=' in tag and tag.find('=')<tag.find(';') else tag for tag in raw.split() )
    raw = raw.replace(',',' ')#.lower()
    tags = raw.split()
    if not tags:
        return ''
    #tags = [ ' '.join(slash_split_tag(tag)) for tag in tags ]
    # slashed-space-separated-string -> extended-space-separated-string:
    tags = flatten_list(map(slash_split_tag, tags)) # [[],[],[]]
    return ' '.join(tags)

def slash_split_tag(tag): # r'blah:a/b\c:d' --> ['blah:a:d', 'blah:b:d', 'blah:c:d']
    tag = tag.replace('\\','/')
    if not '/' in tag:
        return [tag] # no splitting needed
    subtags = tag.split(':')
    pattern, v_pattern = (), ()
    for subtag in subtags:
        if '/' in subtag:
            pattern += (None,)
            v_pattern += (tuple(subtag.split('/')),)
        else:
            pattern += (subtag,)
    def merge_pattern_and_product(pattern, product): # ('x',None,'y',None), ('a','b')
        ret = list(pattern)
        for e in product:
            ret[ret.index(None)] = e
        return ret
    CartesianProduct = tuple(itertools.product(*v_pattern)) # http://stackoverflow.com/a/170248
    #print pattern
    return [ ':'.join(merge_pattern_and_product(pattern, product)) for product in CartesianProduct ]

#def slash_split_tag2(tag): # <-- TOO SIMPLE - DEPRECATED
#    # A/B/C --> A B C
#    # A:1/2 --> A:1 A:2
#    tag = tag.replace('\\','/')
#    if not '/' in tag:
#        return [tag]
#    prefix, splitter, subtags = tag.rpartition(':')
#    subtags = subtags.split('/')
#    return [prefix+splitter+subtag for subtag in subtags]

def matching_tags(tag_1, tag_2): # <-- 'A1:B1','A1:B1/B2' = OK, but 'A1:B1/B2','A1:B1' NOT!!
    if tag_1.count(':') != tag_2.count(':'): return False
    tag1 = tag_1
    tag2 = tag_2
    #if len(tag1) > len(tag2):
    #    buf = tag2[:]
    #    tag1 = tag2[:]
    #    tag2 = buf
    # all subtags must match:
    for i,subtag1 in enumerate(tag1.split(':')):
        return any(( sl1 in tag2.split(':')[i].split('/') for sl1 in subtag1.split('/') ))

def slash_join_tags(splitted_tags): # <-- ['A1:B1','A1:B2','A2:B1','A1']
    #splitted_tags = unsubList(splitted_tags)
    #tags = sorted(splitted_tags)
    tags = subtag_sort(splitted_tags)
    #tags = unsubList(tags)
    joined = [tags[0]]
    j = 0
    buf = list()
    for ti,tag in enumerate(tags[1:]):
        match = matching_tags(joined[j],tag)
        #match = rpart1(joined[j],':') == rpart1(tag,':') # tags can be merged eg: A:1:A & A:1:B
        if match:
            buf.append(tag)
        if ti==len(tags)-2 or not match:
            buf = set([joined[j]]+buf)
            #print 'compr:', buf
            if len(buf) > 1:
                joined[j] = compress_list(buf)
            if not match:
                buf = list()
                joined.append(tag) # next
                j += 1
    joined.sort()
    return joined

def unsubList(lst): # OK
    l = set(lst)
    #l = sorted(list(set(lst)),reverse=True)
    #l = list(l)
    ret = list()
    for s in l:
        not_sub=True
        for e in l:
            if e.startswith(s+':'):
                not_sub=False
                continue # append
        if not_sub:
            ret.append(s)
    #print 'R:',ret
    return ret

def compress_list(alist): # <-- a:b:c a:b:x a:b
    """Compress a list of colon-separated strings into a more compact
    representation.
    """
    #print '1>',alist
    alist = unsubList(alist)
    #print '2>',alist
    #print alist
    # removing sub duplicates
    #print any([l.startswith(l[0]) and alist.count(l) >= 1 for l in alist])
    #alist = [ t for t in alist if not any([l.startswith(t) and alist.count(t) > 1 for l in alist]) ]
    #print alist,'\n\n'
    components = [ss.split(':') for ss in alist]

    # Check that every string in the supplied list has the same number of tags
    tag_counts = [len(cc) for cc in components]
    if len(set(tag_counts)) != 1:
        raise ValueError("Not all of the strings have the same number of tags")

    # For each component, gather a list of all the applicable tags. The set
    # at index k of tag_possibilities is all the possibilities for the
    # kth tag
    tag_possibilities = list()
    for tag_idx in range(tag_counts[0]):
        tag_possibilities.append(set(cc[tag_idx] for cc in components))

    #print '3>',tag_possibilities

    # Now take the list of tags, and turn them into slash-separated strings
    tag_possibilities_strs = ['/'.join(sorted(tt)) for tt in tag_possibilities]

    # Finally, stitch this together with colons
    return ':'.join(tag_possibilities_strs)

def flatten_list(seq): # http://stackoverflow.com/a/952952
    return [ item for subseq in seq for item in subseq ]

def count_sort(seq):
    ret = [(-seq.count(e),e) for e in set(seq)]
    ret.sort()
    return [e[1] for e in ret]

def subtag_sort(seq):
    ret = [(-e.count(':'),e) for e in seq]
    ret.sort()
    return [e[1] for e in ret]

import collections
def flatten_nested_list(l): # http://stackoverflow.com/questions/2158395/flatten-an-irregular-list-of-lists-in-python
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, basestring):
            for sub in flatten_nested_list(el):
                yield sub
        else:
            yield el

def list_i(l,i):
    if not l:
        return False
    return bool(len(l[i:i+1]))

def yN(s):
    return True if s.lower() in ('1','true','yes','y','on','aye','aye!','oi','oi!','ja','naturlich','tak','ta','owszem') else False

def median(mylist):
    sorts = sorted(mylist)
    length = len(sorts)
    if not length % 2:
        return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
    return sorts[length / 2]

# Adapted from: http://www.chimeric.de/blog/2008/0711_smart_dates_in_python
import datetime
def humanize_date_difference(now, otherdate=None, offset=None):
    if otherdate:
        dt = now - otherdate
        offset = dt.seconds + (dt.days * 60*60*24)
    if offset is not None: # is not None !!!!!!!!
        delta_s = offset % 60
        offset /= 60
        delta_m = offset % 60
        offset /= 60
        delta_h = offset % 24
        offset /= 24
        delta_d = offset
    else:
        raise ValueError("Must supply otherdate or offset (from now)")

    if delta_d > 1:
        if delta_d > 6:
            date = now + datetime.timedelta(days=-delta_d, hours=-delta_h, minutes=-delta_m)
            return date.strftime('%A, %Y %B %m, %H:%I')#.encode('utf-8')
        else:
            wday = now + datetime.timedelta(days=-delta_d)
            return wday.strftime('%A')#.encode('utf-8')
    if delta_d == 1:
        return "Yesterday"
    if delta_h > 0:
        return "%dh%dm ago" % (delta_h, delta_m)
    if delta_m > 0:
        return "%dm%ds ago" % (delta_m, delta_s)
    if delta_s > 10:
        return "%ds ago" % delta_s
    else:
        return "just now"