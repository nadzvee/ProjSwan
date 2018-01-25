import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class MoviesGold(Scraper):
    domains = ['moviesgolds.net']
    name = "moviesgold"

    def __init__(self):
        self.base_link = 'http://www.moviesgolds.net'
        self.search_link = ('?s=%s')
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:

            cTitle = cleantitle.get(title)
            query = ('%s-%s' % (cTitle, year))
            url = urlparse.urljoin(self.base_link, query)
            response = client.request(url)

            url = re.findall('''<a\s*href=['\"](http://www\.buzzmovie\.site/\?p=\d+)''', response)[0]

            return self.sources(client.replaceHTMLCodes(url))
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass
        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            srcs = []

            if url == None: return srcs

            try: result = client.request(url, referer=self.base_link)
            except: result = ''

            items = re.findall('''<iframe\s*src=['"]([^'"]+)''', result)
            for item in items:
                try :
                    url = item
                    host = client.host(url)
                    srcs.append({'source': host, 'parts' : '1', 'quality': 'HD', 'scraper': self.name, 'url': url, 'direct':False})
                except :
                    pass
            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            return srcs