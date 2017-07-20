import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class World4U(Scraper):
    domains = ['hdbuffer.com']
    name = "world4u"

    def __init__(self):
        self.base_link = 'https://world4ufree.ws'
        self.search_link = '/?s=%s&feed=rss'
        self.movie_link = '%s/%s/'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            query = '%s %s' % (title, year)
            query = self.search_link % (urllib.quote_plus(query))
            query = urlparse.urljoin(self.base_link, query)

            result = client.request(query)

            result = result.decode('iso-8859-1').encode('utf-8')
            posts = client.parseDOM(result, "item")

            items = []

            for post in posts:
                try :
                    t = client.parseDOM(post, 'title')[0]
                    if 'trailer' in cleantitle.get(t):
                        raise Exception()

                    try: s = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)(?:GB|GiB|MB|MiB|mb|gb))', t)[0]
                    except: s = '0'

                    i = client.parseDOM(post, 'link')[0]

                    items += [{'name':t, 'url':i, 'size':s}]
                except:
                    pass

            title = cleantitle.get(title)
            for item in items:
                try :
                    name = item.get('name')
                    t = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)
                    if cleantitle.get(title) == cleantitle.get(t):
                        y = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()

                        if not y == year: raise Exception()

                        fmt = re.sub('(.+)(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*)(\.|\)|\]|\s)', '', name.upper())
                        fmt = re.split('\.|\(|\)|\[|\]|\s|\-', fmt)
                        fmt = [i.lower() for i in fmt]

                        if any(i.endswith(('subs', 'sub', 'dubbed', 'dub')) for i in fmt): raise Exception()
                        if any(i in ['extras'] for i in fmt): raise Exception()

                        if '1080p' in fmt: quality = '1080p'
                        elif '720p' in fmt: quality = 'HD'
                        else: quality = 'SD'
                        if any(i in ['dvdscr', 'r5', 'r6'] for i in fmt): quality = 'SCR'
                        elif any(i in ['camrip', 'tsrip', 'hdcam', 'hdts', 'dvdcam', 'dvdts', 'cam', 'telesync', 'ts'] for i in fmt): quality = 'CAM'

                        info = []

                        if '3d' in fmt: info.append('3D')

                        try:
                            size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+)(?:GB|GiB|MB|MiB|mb|gb))', item.get('size'))[-1]
                            div = 1 if size.endswith(('GB', 'GiB')) else 1024
                            size = float(re.sub('[^0-9|/.|/,]', '', size))/div
                            size = '%.2f GB' % size
                            info.append(size)
                        except:
                            pass

                        if any(i in ['hevc', 'h265', 'x265'] for i in fmt): info.append('HEVC')

                        info = ' | '.join(info)

                        movieurl = item.get('url')

                        result = client.request(movieurl)
                        result = result.decode('iso-8859-1').encode('utf-8')
                        result = result.replace('\n','').replace('\t','')

                        result = client.parseDOM(result, 'div', attrs={'class':'entry'})[0]
                        links = client.parseDOM(result, 'a',attrs={'target':'_blank'}, ret='href')

                        for link in links:
                            if 'http' in link:
                                host = client.host(link)

                                self.srcs.append({'source': host, 'parts': '1', 'quality': quality, 'scraper':self.name, 'url': link, 'direct':False, 'info':info})
                except:
                    pass
            logger.debug('SOURCES [%s]' % self.srcs, __name__)
            return self.srcs
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass
        return []