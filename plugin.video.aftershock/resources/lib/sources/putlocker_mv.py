# -*- coding: utf-8 -*-

'''
    Exodus Add-on
    Copyright (C) 2016 Exodus

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


import re,urllib,urlparse,base64, time, json

from resources.lib.libraries import client
from resources.lib.libraries import logger
from resources.lib.libraries import directstream

class source:
    def __init__(self):
        self.domains = ['putlocker.systems', 'putlocker-movies.tv', 'putlocker.yt', 'cartoonhd.website']
        self.base_link = 'http://cartoonhd.website'

    def get_movie(self, imdb, title, year):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return url
        except:
            return

    def get_sources(self, url):
        logger.debug('[%s] SOURCES URL %s' % (self.__class__, url))

        try:
            sources = []

            if url == None: return sources

            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['title']

                imdb = data['imdb']

                match = (title.translate(None, '\/:*?"\'<>|!,')).replace(' ', '-').replace('--', '-').lower()

                url = '%s/movie/%s' % (self.base_link, match)

                result = client.request(url, limit='5')
                result = client.parseDOM(result, 'title')[0]

                if '%TITLE%' in result: raise Exception()

                r = client.request(url, output='extended')

                if not imdb in r[0]: raise Exception()


            else:

                url = urlparse.urljoin(self.base_link, url)

                r = client.request(url, output='extended')


            cookie = r[4] ; headers = r[3] ; result = r[0]

            try: auth = re.findall('__utmx=(.+)', cookie)[0].split(';')[0]
            except: auth = 'false'
            auth = 'Bearer %s' % urllib.unquote_plus(auth)

            headers['Authorization'] = auth
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            headers['Cookie'] = cookie
            headers['Referer'] = url


            u = '/ajax/nembeds.php'
            u = urlparse.urljoin(self.base_link, u)

            action = 'getEpisodeEmb' if '/episode/' in url else 'getMovieEmb'

            elid = urllib.quote(base64.encodestring(str(int(time.time()))).strip())

            token = re.findall("var\s+tok\s*=\s*'([^']+)", result)[0]

            idEl = re.findall('elid\s*=\s*"([^"]+)', result)[0]

            post = {'action': action, 'idEl': idEl, 'token': token, 'elid': elid}
            post = urllib.urlencode(post)

            r = client.request(u, post=post, headers=headers)
            r = str(json.loads(r))
            r = client.parseDOM(r, 'iframe', ret='.+?') + client.parseDOM(r, 'IFRAME', ret='.+?')


            links = []

            for i in r:
                try: links += [{'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'url': i, 'direct': True}]
                except: pass

            links += [{'source': 'openload.co', 'quality': 'SD', 'url': i, 'direct': False} for i in r if 'openload.co' in i]

            for i in links: sources.append({'source': i['source'], 'quality': i['quality'], 'provider': 'Putlocker', 'url': i['url'], 'direct': i['direct'], 'debridonly': False})

            logger.debug('[%s] SOURCES [%s]' % (__name__,sources))
            return sources
        except:
            return sources

    def resolve(self, url, resolverList=None):
        return url