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


import re,urllib,urlparse,datetime, random

from resources.lib.libraries import cleantitle
from resources.lib.libraries import client
from resources.lib import resolvers
from resources.lib.libraries import metacache

class source:
    def __init__(self):
        self.base_link = 'http://www.desihit.net'
        self.search_str_link = '/front/search.php?q=%s'
        self.search_link = '/front/controller.php?action=searchthis&searchbox=%s'
        self.movie_link = '/front/controller.php?action=showMovieDetail&movieId=%s'
        self.sort_link = '&order=desc&sort=date'
        self.langMap = {'hindi':'hi', 'tamil':'ta', 'telugu':'te','ml':'malayalam', 'kn':'kannada', 'bn':'bengali', 'mr':'marathi', 'pa':'punjabi'}

    def get_movie(self, imdb, title, year):
        try:
            self.base_link = self.base_link
            query = '%s (%s)' % (title, year)
            query = self.search_str_link % (urllib.quote_plus(query))
            query = urlparse.urljoin(self.base_link, query)

            result = client.source(query)

            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.split("\n")

            searchString = result[0]
            query = self.search_link % urllib.quote_plus(searchString)
            query = urlparse.urljoin(self.base_link, query)
            result = client.source(query)

            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, "div", attrs={"id":"content"})[0]
            result = client.parseDOM(result, "table")[0]
            result = client.parseDOM(result, "tr")

            title = cleantitle.movie(searchString)

            for item in result:
                item = client.parseDOM(item, "td", attrs={"width":"89%"})[0]
                searchTitle = client.parseDOM(item, "a")[0]
                searchTitle = cleantitle.movie(searchTitle)
                if title == searchTitle:
                    url = client.parseDOM(item, "a", ret="href")[0]
                    url = re.compile("movieId=(.+?)&").findall(url)[0]
                    break
            if url == None or url == '':
                raise Exception()
            return url
        except:
            return

    def get_sources(self, url):
        try:
            quality = ''
            sources = []

            if url == None: return sources

            url = self.movie_link % url
            url = urlparse.urljoin(self.base_link, url)

            try: result = client.source(url, referer=url)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.replace('\n','').replace('\t','')

            result = client.parseDOM(result, "div", attrs={"class":"movierip"})

            for item in result:
                try :
                    urls = client.parseDOM(item, "a", ret="href")
                    quality = client.parseDOM(item, "a")[0]
                    quality = quality.lower()
                    if "scr rip" in quality:
                        quality = "SCR"
                    elif "dvd" in quality :
                        quality = "HD"
                    else:
                        quality = "CAM"

                    for i in range(0, len(urls)):
                        item = client.source(urls[i], referer=url)
                        item = client.parseDOM(item, "td", attrs={"valign":"top", "align":"center"})[0]
                        item = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(item)[0][1]
                        urls[i] = item
                    host = client.host(urls[0])
                    if len(urls) > 1:
                        url = "##".join(urls)
                    else:
                        url = urls[0]
                    sources.append({'source': host, 'parts' : str(len(urls)), 'quality': quality, 'provider': 'DesiHit', 'url': url, 'direct':False})
                except :
                    pass
            return sources
        except:
            return sources


    def resolve(self, url, resolverList):
        try:
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
            return url
        except:
            return False