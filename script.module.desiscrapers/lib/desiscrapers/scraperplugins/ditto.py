import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class Ditto(Scraper):
    domains = ['dittotv.com']
    name = "ditto"

    def __init__(self):
        self.base_link = 'http://www.dittotv.com'
        self.search_link = 'search?q=%s'
        self.info_link = '/catalog/movie/%s/cc=US'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            query = title
            query = self.search_link % (urllib.quote_plus(query))
            query = urlparse.urljoin(self.base_link,query)

            result = client.request(query)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = client.parseDOM(result, "div", attrs={"class": "result clearfix"})

            cleanedTitle = cleantitle.get(title)

            for item in result:

                item = client.parseDOM(item, "div", attrs={"class": "details"})[0]

                linkTitle = client.parseDOM(item, "a")[0]

                if cleanedTitle == cleantitle.get(linkTitle):
                    url = client.parseDOM(item, "a", ret="href")[0]
                    break

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

            oUrl = urlparse.urljoin(self.base_link, url)
            try: result = client.request(oUrl)
            except: result = ''

            url = client.parseDOM(result, "div", attrs={"class": "video-wrapper"})[0]
            url = client.parseDOM(url, "source", ret="src")[0]
            url = '%s|Referer=%s' % (url, oUrl)

            #host = client.host(url)

            srcs.append({'source': 'ditto', 'parts': '1', 'quality': "HD", 'scraper': self.name, 'url': url, 'direct':True})

            logger.debug('SOURCES [%s]' % srcs, __name__)

            return srcs
        except:
            pass