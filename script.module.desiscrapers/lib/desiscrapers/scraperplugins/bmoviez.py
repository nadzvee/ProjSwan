import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class BMoviez(Scraper):
    domains = ['best-moviez.ws']
    name = "bmoviez"

    def __init__(self):
        self.base_link = 'http://www.best-moviez.ws'
        self.search_link = '/feed/rss2/?s=%s'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            url = {'imdb': imdb, 'title': title, 'year': year}
            url = urllib.urlencode(url)
            return []
            return self.sources(client.replaceHTMLCodes(url))
        except:
            pass
        return []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            url = {'tvshowtitle': title, 'season': season, 'episode': episode, 'imdb':imdb, 'tvdb':tvdb, 'year':year}
            url = urllib.urlencode(url)
            return self.sources(client.replaceHTMLCodes(url))
        except:
            pass
        return []

    def sources(self, url):
        try:
            logger.debug('SOURCES URL %s' % url, __name__)

            if url == None: return []

            data = urlparse.parse_qs(url)
            data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

            title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']

            cleanedTitle = cleantitle.get(title)

            hdlr = 'S%02dE%02d' % (int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else data['year']

            query = '%s S%02dE%02d' % (data['tvshowtitle'], int(data['season']), int(data['episode'])) if 'tvshowtitle' in data else '%s %s' % (data['title'], data['year'])
            query = re.sub('(\\\|/| -|:|;|\*|\?|"|\'|<|>|\|)', ' ', query)

            url = self.search_link % urllib.quote_plus(query)
            url = urlparse.urljoin(self.base_link, url)

            r = client.request(url)

            posts = client.parseDOM(r, 'item')

            items = []

            for post in posts:
                try:
                    t = client.parseDOM(post, 'title')[0]
                    post = post.replace('\n','').replace('\t','')
                    post = re.compile('<span style="color: #ff0000">Single Link</b></span><br />(.+?)<span style="color: #ff0000">').findall(post)[0]
                    u = re.findall('<a href="(http(?:s|)://.+?)">', post)
                    items += [(t, i) for i in u]
                except:
                    pass

            for item in items:
                try:
                    name = client.replaceHTMLCodes(item[0])

                    linkTitle = re.sub('(\.|\(|\[|\s)(\d{4}|S\d*E\d*|S\d*|3D)(\.|\)|\]|\s|)(.+|)', '', name)

                    if not cleanedTitle == cleantitle.get(linkTitle): raise Exception()

                    year = re.findall('[\.|\(|\[|\s](\d{4}|S\d*E\d*|S\d*)[\.|\)|\]|\s]', name)[-1].upper()

                    if not year == hdlr: raise Exception()

                    self.source(item)
                except:
                    pass

            logger.debug('SOURCES [%s]' % self.srcs, __name__)
            return self.srcs
        except:
            return self.srcs

    def source(self, item):

        name = client.replaceHTMLCodes(item[0])

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
            size = re.findall('((?:\d+\.\d+|\d+\,\d+|\d+) [M|G]B)', name)[-1]
            div = 1 if size.endswith(' GB') else 1024
            size = float(re.sub('[^0-9|/.|/,]', '', size))/div
            size = '%.2f GB' % size
            info.append(size)
        except:
            pass

        if any(i in ['hevc', 'h265', 'x265'] for i in fmt): info.append('HEVC')

        info = ' | '.join(info)

        url = item[1]
        if any(x in url for x in ['.rar', '.zip', '.iso']): raise Exception()
        url = client.replaceHTMLCodes(url)
        url = url.encode('utf-8')

        host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
        host = client.replaceHTMLCodes(host)
        host = host.encode('utf-8')

        self.srcs.append({'source': host, 'parts': '1', 'quality': quality, 'provider': self.name, 'url': url, 'info': info, 'direct': False, 'debridonly': True})
