import re
import urllib
import urlparse
import base64

from aftershock.common import cleantitle, client, logger, proxy
from ..scraper import Scraper


class WatchFree(Scraper):
    domains = ['watchfree.to']
    name = "watchfree"

    def __init__(self):
        self.base_link = 'http://gowatchfreemovies.to'
        self.moviesearch_link = '/?keyword=%s&search_section=1'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            query = self.moviesearch_link % urllib.quote_plus(cleantitle.query(title))
            query = urlparse.urljoin(self.base_link, query)

            result = str(proxy.request(query, 'item'))
            if 'page=2' in result or 'page%3D2' in result: result += str(proxy.request(query + '&page=2', 'item'))

            result = client.parseDOM(result, 'div', attrs = {'class': 'item'})

            title = 'watchputlocker' + cleantitle.get(title)
            years = ['(%s)' % str(year), '(%s)' % str(int(year)+1), '(%s)' % str(int(year)-1)]

            result = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'a', ret='title')) for i in result]
            result = [(i[0][0], i[1][0]) for i in result if len(i[0]) > 0 and len(i[1]) > 0]
            result = [i for i in result if any(x in i[1] for x in years)]

            r = [(proxy.parse(i[0]), i[1]) for i in result]

            match = [i[0] for i in r if title == cleantitle.get(i[1]) and '(%s)' % str(year) in i[1]]

            match2 = [i[0] for i in r]
            match2 = [x for y,x in enumerate(match2) if x not in match2[:y]]
            if match2 == []: return

            for i in match2[:5]:
                try:
                    if len(match) > 0: url = match[0] ; break
                    r = proxy.request(urlparse.urljoin(self.base_link, i), 'link_ite')
                    r = re.findall('(tt\d+)', r)
                    if imdb in r: url = i ; break
                except:
                    pass

            url = re.findall('(?://.+?|)(/.+)', url)[0]
            url = client.replaceHTMLCodes(url)
            url = url.encode('utf-8')
            return self.sources(client.replaceHTMLCodes(url))
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass
        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            quality = ''
            srcs = []

            if url == None: return srcs

            url = urlparse.urljoin(self.base_link, url)

            result = proxy.request(url, 'link_ite')

            links = client.parseDOM(result, 'table', attrs = {'class': 'link_ite.+?'})

            for i in links:
                try:
                    url = client.parseDOM(i, 'a', ret='href')
                    url = [x for x in url if 'gtfo' in x][-1]
                    url = proxy.parse(url)
                    url = urlparse.parse_qs(urlparse.urlparse(url).query)['gtfo'][0]
                    url = base64.b64decode(url)
                    url = client.replaceHTMLCodes(url)
                    url = url.encode('utf-8')

                    host = re.findall('([\w]+[.][\w]+)$', urlparse.urlparse(url.strip().lower()).netloc)[0]
                    host = host.encode('utf-8')

                    quality = client.parseDOM(i, 'div', attrs = {'class': 'quality'})
                    if any(x in ['[CAM]', '[TS]'] for x in quality): quality = 'CAM'
                    else:  quality = 'SD'
                    quality = quality.encode('utf-8')

                    srcs.append({'source': host, 'parts':'1', 'quality': quality, 'scraper':self.name, 'url': url, 'direct': False})
                except:
                    pass

            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs