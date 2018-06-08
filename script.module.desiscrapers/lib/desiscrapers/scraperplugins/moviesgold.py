import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class MoviesGold(Scraper):
    domains = ['movgold.net']
    name = "moviesgold"

    def __init__(self):
        self.base_link = 'http://www.movgold.net'
        self.search_link = ('search/%s/feed/rss2')
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:

            cleanedTitle = cleantitle.get(title)
            query = '%s %s' % (title, year)
            query = self.search_link % (urllib.quote_plus(query))
            url = urlparse.urljoin(self.base_link, query)
            result = client.request(url)

            result = result.decode('iso-8859-1').encode('utf-8')

            items = client.parseDOM(result, "item")

            for item in items:
                linkTitle = client.parseDOM(item, 'title')[0]

                try :
                    parsed = re.compile('(.+?) \((\d{4})\) ').findall(linkTitle)[0]
                    parsedTitle = parsed[0]
                    parsedYears = parsed[1]
                except: pass

                if cleanedTitle == cleantitle.get(parsedTitle):
                    url = client.parseDOM(item, "link")[0]
                    self.sources(client.replaceHTMLCodes(url))

            return self.srcs
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass
        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            if url == None: return self.srcs

            try: result = client.request(url, referer=self.base_link)
            except: result = ''

            items = client.parseDOM(result, "source", ret="src")
            for item in items:
                try :
                    url = item
                    host = client.host(url)
                    self.srcs.append({'source': host, 'parts' : '1', 'quality': 'HD', 'scraper': self.name, 'url': url, 'direct':False})
                except :
                    pass
            logger.debug('SOURCES [%s]' % self.srcs, __name__)
            return self.srcs
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            return self.srcs