# -*- coding: utf-8 -*-

'''
    Aftershock Common Add-on
    Copyright (C) 2017 Aftershockpy

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import re
import unicodedata
import HTMLParser

from . import control

try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database

def unicodetoascii(text):

    uni2ascii = {
        ord('\xe2\x80\x99'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\x9c'.decode('utf-8')): ord('"'),
        ord('\xe2\x80\x9d'.decode('utf-8')): ord('"'),
        ord('\xe2\x80\x9e'.decode('utf-8')): ord('"'),
        ord('\xe2\x80\x9f'.decode('utf-8')): ord('"'),
        ord('\xc3\xa9'.decode('utf-8')): ord('e'),
        ord('\xe2\x80\x9c'.decode('utf-8')): ord('"'),
        ord('\xe2\x80\x93'.decode('utf-8')): ord('-'),
        ord('\xe2\x80\x92'.decode('utf-8')): ord('-'),
        ord('\xe2\x80\x94'.decode('utf-8')): ord('-'),
        ord('\xe2\x80\x94'.decode('utf-8')): ord('-'),
        ord('\xe2\x80\x98'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\x9b'.decode('utf-8')): ord("'"),

        ord('\xe2\x80\x90'.decode('utf-8')): ord('-'),
        ord('\xe2\x80\x91'.decode('utf-8')): ord('-'),

        ord('\xe2\x80\xb2'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\xb3'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\xb4'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\xb5'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\xb6'.decode('utf-8')): ord("'"),
        ord('\xe2\x80\xb7'.decode('utf-8')): ord("'"),

        ord('\xe2\x81\xba'.decode('utf-8')): ord("+"),
        ord('\xe2\x81\xbb'.decode('utf-8')): ord("-"),
        ord('\xe2\x81\xbc'.decode('utf-8')): ord("="),
        ord('\xe2\x81\xbd'.decode('utf-8')): ord("("),
        ord('\xe2\x81\xbe'.decode('utf-8')): ord(")"),

    }
    return text.decode('utf-8').translate(uni2ascii).encode('ascii')

def geturl(title):
    if title == None: return
    title = title.lower()
    title = title.translate(None, ':*?"\'\.<>|&!,')
    title = title.replace('/', '-')
    title = title.replace(' ', '-')
    title = title.replace('--', '-')
    return title

def get(title):
    if title == None: return
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|([[].+?[]])|([(].+?[)])|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title

def get_search(title):
    if title == None: return
    title = title.lower()
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\\\|/|\(|\)|\[|\]|\{|\}|-|:|;|\*|\?|"|\'|<|>|\_|\.|\?', ' ', title).lower()
    title = ' '.join(title.split())
    return title

def get_simple(title):
    if title == None: return
    title = title.lower()
    title = re.sub('(\d{4})', '', title)
    title = re.sub('&#(\d+);', '', title)
    title = re.sub('(&#[0-9]+)([^;^0-9]+)', '\\1;\\2', title)
    title = title.replace('&quot;', '\"').replace('&amp;', '&')
    title = re.sub('\n|\(|\)|\[|\]|\{|\}|\s(vs|v[.])\s|(:|;|-|"|,|\'|\_|\.|\?)|\s', '', title).lower()
    return title


def query(title):
    if title == None: return
    title = title.replace('\'', '').rsplit(':', 1)[0]
    return title


def normalize(title):
    try:
        try: return title.decode('ascii').encode("utf-8")
        except: pass

        return str( ''.join(c for c in unicodedata.normalize('NFKD', unicode( title.decode('utf-8') )) if unicodedata.category(c) != 'Mn') )
    except:
        return title