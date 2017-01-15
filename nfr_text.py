#!/usr/bin/python
# -*- coding: utf-8 -*-

from terminalsize import get_terminal_size # https://gist.github.com/jtriley/1108174
consoleX, consoleY = get_terminal_size()

def center_text(text, width=consoleX):
    formatted = list()
    lines = text.split('\n')
    for line in lines:
        formatted.append(' '*((width-len(strip_esc(line)))/2-1)+line)
    return '\n'.join(formatted)

import sys

class Looper(object):
    def __init__(self, animation=('-','\\','|','/'), text=''):
        self.animation = animation
        if isinstance(animation, str):
            if   animation == 'star':   self.animation = tuple('-\\|/')
            elif animation == 'ball': self.animation = ('[o   ]','[ o  ]','[  o ]','[   o]','[  o ]','[ o  ]')
            elif animation == 'marquee': self.animation = tuple(' '+' '*i+text+' '*(consoleX-2-i-len(text)) for i in xrange(consoleX-2-len(text)))
            elif animation == 'stick': self.animation = tuple(' '+' '*i+text[i%len(text)-1]+' '*(consoleX-2-i-1) for i in xrange(consoleX-2-1))
            else:
                _ = consoleX-1 - len(animation)
                self.animation = [' '*i+animation+' '*(_-1-i) for i in xrange(_)]
        self.frame = 0
        self.total_frames = len(self.animation)
        self.wrote = None
    def animate(self, suffix='', prefix='', interval=1, embed=None): # embed is for use in generators
        to_write = '\r%s' % prefix+self.animation[(self.frame/interval) % self.total_frames][len(prefix):consoleX-len(suffix)-1]+suffix
        if to_write != self.wrote:
            sys.stdout.write(to_write)
            sys.stdout.flush()
            self.wrote = to_write
        self.frame += 1
        return embed
    def next_iteration(self):
        self.frame += 1
        return self.frame
    def reset(self):
        self.frame = 0
        self.wrote = None

def clrln(and_write=''): # clear line
    sys.stdout.write('\r'+' '*(get_terminal_size()[0]-1)+'\r'+and_write)
    sys.stdout.flush()

import re

#ansi_pattern = '\033\[((?:\d|;)*)([a-zA-Z])'
#ansi_pattern = '\x1b.*?m'
ansi_pattern = r'\x1b[^m]*m'
#ansi_pattern = '\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?'
ansi_escape = re.compile(ansi_pattern)
#ansi_escape = re.compile(r'\x1b[^m]*m')
def strip_esc(s):
    return ansi_escape.sub('', s)

from textwrap import TextWrapper as tw # https://docs.python.org/2/library/textwrap.html
#wrapped = wrap(width=consoleX-1).fill
def definition(subject, text, width=None):
    #text = text.replace('\n','')
    if width is None:
        width = get_terminal_size()[0]
    #return tw(width-1, subsequent_indent=' '*(len(strip_esc(subject))+1)).fill(subject+' '+text)
    return tw(width-1, subsequent_indent=' '*(len(strip_esc(subject))+1)).fill(subject+' '+text)

def get_ansi_and_pos(ansi_string): # returns [(ansi_code(str), position(int)), ...]
    ansi__pos = list()
    for match in ansi_escape.finditer(ansi_string):
        ansi__pos.append((match.group(0), match.start()))
    return ansi__pos
from textwrap import wrap
import os
def wrap_ansi(ansi_string, width=None, ident='', break_char=None):
    global consoleX
    if width is None or width < 1: width = consoleX
    width -= len(strip_esc(ident)) + 1
    ansi__pos = get_ansi_and_pos(ansi_string)
    ascii_string = strip_esc(ansi_string)
    wrapped_ascii = wrap(ascii_string, width)
    wrapped_ansi = wrapped_ascii[:]
    #pos = 0
    #print(ansi__pos)
    while ansi__pos:
        ansi, start = ansi__pos.pop(0)
        pos = 0
        #print(ansi, start)
        #ansi = '\033['+ansi+'m'
        for line_i,line in enumerate(wrapped_ansi):
            for i,c in enumerate(line):
                if pos == start:
                    x = i - line_i# + (1 if line_i > 1 else 0)# ?
                    wrapped_ansi[line_i] = line[:x]+ansi+line[x:]
                    ansi = None
                    break
                #if strip_esc(c):
                pos += 1
                #print(pos)
            if not ansi:
                break
    #print(wrapped_ansi)
    if ident:
        spaces = ' '*len(strip_esc(ident))
        for i, line in enumerate(wrapped_ansi):
            if i == 0:
                wrapped_ansi[0] = ident + line
            else:
                wrapped_ansi[i] = spaces + line
    if break_char is None:
        wrapped_ansi = os.linesep.join(wrapped_ansi)
        #wrapped_ansi = '\033[10m'.join(wrapped_ansi)
    else:
        wrapped_ansi = break_char.join(wrapped_ansi)
    return wrapped_ansi

def ansi_definition(subject, text, width=None):
    return wrap_ansi(text, width, subject)

def gotoxy(x,y): # ansi code: move cursor to x,y
    sys.stdout.write('\033['+str(x)+';'+str(y)+'H')
    sys.stdout.flush()
