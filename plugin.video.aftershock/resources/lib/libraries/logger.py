# -*- coding: utf-8 -*-

'''
    Copyright (C) 2015 IDev

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


import os,xbmc, logging

from resources.lib.libraries import control

LOGDEBUG = xbmc.LOGDEBUG
LOGERROR = xbmc.LOGERROR
LOGFATAL = xbmc.LOGFATAL
LOGINFO = xbmc.LOGINFO
LOGNONE = xbmc.LOGNONE
LOGNOTICE = xbmc.LOGNOTICE
LOGSEVERE = xbmc.LOGSEVERE
LOGWARNING = xbmc.LOGWARNING

name = control.addonInfo('name')
version = control.addonInfo('version')

def debug(msg):
    log(msg, level=LOGDEBUG)

def notice(msg):
    log(msg, level=LOGNOTICE)

def warning(msg):
    log(msg, level=LOGWARNING)

def error(msg):
    log(msg, level=LOGERROR)

def log(msg, level=LOGDEBUG):
    # override message level to force logging when addon logging turned on
    if control.setting('debug') == 'true' and level == LOGDEBUG:
        level = LOGNOTICE

    try:
        if isinstance(msg, unicode):
            msg = '%s (ENCODED)' % (msg.encode('utf-8'))

        xbmc.log('%s (%s): %s' % (name, version, msg), level)
    except Exception as e:
        try: xbmc.log('Logging Failure: %s' % (e), level)
        except: pass  # just give up