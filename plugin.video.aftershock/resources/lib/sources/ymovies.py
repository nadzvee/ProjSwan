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

import base64
import json
import random
import re
import string
import urllib
import urlparse

from ashock.modules import cache
from ashock.modules import client
from ashock.modules import cleantitle


class source:
    def __init__(self):
        self.domains = ['yesmovies.to']
        self.base_link = 'http://yesmovies.to'
        self.info_link = 'http://yesmovies.to/'
        self.playlist = '/ajax/v2_get_sources/%s.html?hash=%s'
        self.key1 = base64.b64decode('eHdoMzhpZjM5dWN4')
        self.key2 = base64.b64decode('OHFoZm05b3lxMXV4')
        self.key = base64.b64decode('Y3RpdzR6bHJuMDl0YXU3a3F2YzE1M3Vv')

    def movie(self, imdb, title, year):
        self.super_url = []
        try:
            self.super_url = []
            title = cleantitle.getsearch(title)
            cleanmovie = cleantitle.get(title)
            query = "/search/%s.html" % (urllib.quote_plus(title))
            query = urlparse.urljoin(self.base_link, query)
            link = client.request(query)
            r = client.parseDOM(link, 'div', attrs={'class': 'ml-item'})
            for links in r:
                # print ("YMOVIES REQUEST", links)
                url = client.parseDOM(links, 'a', ret='data-url')[0]
                title = client.parseDOM(links, 'a', ret='title')[0]
                url = urlparse.urljoin(self.info_link, url)
                infolink = client.request(url)
                match_year = re.search('class="jt-info">(\d{4})<', infolink)
                match_year = match_year.group(1)
                if year in match_year:
                    result = client.parseDOM(infolink, 'div', attrs={'class': 'jtip-bottom'})
                    for items in result:
                        playurl = client.parseDOM(items, 'a', ret='href')[0]
                        playurl = playurl.encode('utf-8')
                        referer = "%s" % playurl

                        mylink = client.request(referer)
                        i_d = re.findall(r'id: "(.*?)"', mylink, re.I | re.DOTALL)[0]
                        server = re.findall(r'server: "(.*?)"', mylink, re.I | re.DOTALL)[0]
                        type = re.findall(r'type: "(.*?)"', mylink, re.I | re.DOTALL)[0]
                        episode_id = re.findall(r'episode_id: "(.*?)"', mylink, re.I | re.DOTALL)[0]
                        # print ("YMOVIES REQUEST", episode_id)
                        token = self.__get_token()
                        # print ("YMOVIES TOKEN", token)
                        cookies = '%s%s%s=%s' % (self.key1, episode_id, self.key2, token)
                        # print ("YMOVIES cookies", cookies)
                        url_hash = urllib.quote(self.__uncensored(episode_id + self.key, token))
                        # print ("YMOVIES hash", url_hash)
                        url = urlparse.urljoin(self.base_link, self.playlist % (episode_id, url_hash))

                        request_url = url
                        # print ("YMOVIES REQUEST", request_url)
                        self.super_url.append([request_url, cookies, referer])
            return self.super_url
        except:
            return

    def sources(self, url):
        try:
            srcs = []
            for movielink, cookies, referer in url:
                # print ("YMOVIES SOURCES", movielink, cookies, referer)
                headers = {'Referer': referer,
                           'User-Agent': cache.get(client.randomagent, 1),
                           'X-Requested-With': 'XMLHttpRequest'}
                result = client.request(movielink, headers=headers, cookie=cookies)
                result = json.loads(result)
                # print ("YMOVIES SOURCE PLAYLIST", result)
                links = result['playlist'][0]['sources']
                for item in links:
                    videoq = item['label']
                    url = item['file']
                    if "1080" in videoq:
                        quality = "1080p"
                    elif "720" in videoq:
                        quality = "HD"
                    else:
                        quality = "SD"
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    srcs.append(
                        {'source': 'gvideo', 'quality': quality, 'provider': 'Ymovies', 'url': url, 'direct': True,
                         'debridonly': False})
            return srcs
        except:
            return srcs

    def resolve(self, url, resolverList):
        if 'requiressl=yes' in url:
            url = url.replace('http://', 'https://')
        else:
            url = url.replace('https://', 'http://')
        return url

    ################### CREDITS FOR TKNORRIS for this FIXES ##############################

    def __get_token(self):
        return ''.join(random.sample(string.digits + string.ascii_lowercase, 6))

    def __uncensored(self, a, b):
        c = ''
        i = 0
        for i, d in enumerate(a):
            e = b[i % len(b) - 1]
            d = int(self.__jav(d) + self.__jav(e))
            c += chr(d)

        return base64.b64encode(c)

    def __jav(self, a):
        b = str(a)
        code = ord(b[0])
        if 0xD800 <= code and code <= 0xDBFF:
            c = code
            if len(b) == 1:
                return code
            d = ord(b[1])
            return ((c - 0xD800) * 0x400) + (d - 0xDC00) + 0x10000

        if 0xDC00 <= code and code <= 0xDFFF:
            return code
        return code
