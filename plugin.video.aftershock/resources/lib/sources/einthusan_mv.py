# -*- coding: utf-8 -*-

'''
    Aftershock Add-on
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


import re,urllib,urlparse,json

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib.libraries import logger

class source:
    def __init__(self):
        self.base_link = 'http://www.einthusan.com'
        self.search_link = '/webservice/filters.php'
        self.movie_link = '/webservice/movie.php?id=%s'

    def get_movie(self, imdb, title, year):
        try:
            langMap = {'hi':'hindi', 'ta':'tamil', 'te':'telugu', 'ml':'malayalam', 'kn':'kannada', 'bn':'bengali', 'mr':'marathi', 'pa':'punjabi'}

            lang = 'http://www.imdb.com/title/%s/' % imdb
            lang = client.request(lang)
            lang = re.findall('href\s*=\s*[\'|\"](.+?)[\'|\"]', lang)
            lang = [i for i in lang if 'language=' in i]
            lang = [i.split('language=')[-1].split('&')[0].lower() for i in lang]
            lang = [i for i in lang if any(x == i for x in langMap.keys())]
            lang = langMap[lang[0]]


            url = urlparse.urljoin(self.base_link, self.search_link)
            post = urllib.urlencode({'search': title, 'lang': lang})

            result = client.request(url, post=post)
            result = json.loads(result)['results'][:2]
            result = [urlparse.urljoin(self.base_link, self.movie_link % i) for i in result]

            title = cleantitle.movie(title)
            years = ['%s' % str(year)]

            url = None

            info = json.loads(client.request(result[0]))
            if title == cleantitle.movie(info['movie']) and any(x in str(info['year']) for x in years): url = info['movie_id']

            if url == None: info = json.loads(client.request(result[1]))
            if title == cleantitle.movie(info['movie']) and any(x in str(info['year']) for x in years): url = info['movie_id']

            if url == None: return

            url = str(url)
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return url
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            return

    def get_sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            sources = []

            if url == None: return sources

            try: import xbmc ; ip = xbmc.getIPAddress()
            except: ip = 'London'

            referer = 'http://www.einthusan.com/movies/watch.php?id=%s' % url

            agent = client.randomagent()

            headers = {'User-Agent': agent, 'Referer': referer}

            url = 'http://cdn.einthusan.com/geturl/%s/hd/%s/' % (url, ip)
            url = client.request(url, headers=headers)

            url +='|%s' % urllib.urlencode({'User-agent': agent})

            #url = '%s|Referer=%s&User-Agent=%s' % (url, url, client.getDefaultUserAgent())

            sources.append({'source': 'einthusan', 'parts' : '1','quality': 'HD', 'provider': 'Einthusan', 'url': url,'direct':True})
            logger.debug('SOURCES [%s]' % sources, __name__)
            return sources
        except:
            return sources

    def resolve(self, url, resolverList):
        return url