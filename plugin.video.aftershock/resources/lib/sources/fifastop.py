# -*- coding: utf-8 -*-

'''
    Aftershock Add-on
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
import urllib
import urlparse

from resources.lib import resolvers
from ashock.modules import client
from ashock.modules import logger
from ashock.modules import cleantitle


class source:
    def __init__(self):
        self.base_link_1 = 'http://www.fifastop.com'
        self.base_link_2 = self.base_link_1
        self.base_link_3 = self.base_link_2

        self.search_link = '/search.php?keywords=%s'

        self.srcs = []

    def tvshow(self, tvshowurl, imdb, tvdb, tvshowtitle, year):
        if tvshowurl:
            return tvshowtitle

    def episode(self, url, ep_url, imdb, tvdb, title, date, season, episode):
        try :
            query = '%s %s' % (url, title)
            cTitle = query
            query = self.search_link % (urllib.quote_plus(query))

            links = [self.base_link_1, self.base_link_2, self.base_link_3]
            for base_link in links:
                try: result = client.request(base_link + '/' + query)
                except: result = ''
                if 'pm-li-video' in result: break

            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.replace('\n','').replace('\t','')

            items = client.parseDOM(result, "div", attrs={"class":"pm-li-video"})

            for item in items:
                item = client.parseDOM(item, "h3")[0]
                sUrl = client.parseDOM(item, "a", ret="href")[0]
                sTitle = client.parseDOM(item, "a", ret="title")[0]
                t1 = cleantitle.get(cTitle)
                t2 = cleantitle.get(sTitle)
                if cleantitle.get(cTitle) == cleantitle.get(sTitle) :
                    ep_url = sUrl
                    break
        except:
            ep_url = None
            pass

        if ep_url :
            return ep_url

    def sources(self, url):
        try:
            logger.debug('SOURCES URL %s' % url, __name__)
            quality = ''
            srcs = []

            quality = 'HD'
            host = client.host(url)
            srcs.append({'source':host, 'parts': '1', 'quality':quality,'provider':'fifastop','url':url, 'direct':False})

            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs

    def resolve(self, url, resolverList):
        try:
            logger.debug('ORIGINAL URL [%s]' % url, __name__)
            tUrl = url.split('##')
            if len(tUrl) > 0:
                url = tUrl
            else :
                url = urlparse.urlparse(url).path

            links = []
            for item in url:
                r = resolvers.request(item, resolverList)
                if not r :
                    raise Exception()
                links.append(r)
                url = links
            logger.debug('RESOLVED URL [%s]' % url, __name__)
            return url
        except:
            return False