import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class CineVood(Scraper):
    domains = ['cinevood.net']
    name = "cinevood"

    def __init__(self):
        self.base_link = 'http://cinevood.net'
        self.search_link = '/feed?s=%s'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            query = '%s' % (title)
            query = self.search_link % (urllib.quote_plus(query))
            query = urlparse.urljoin(self.base_link, query)
            cleanedTitle = cleantitle.get(title)

            result = client.request(query)

            result = result.decode('iso-8859-1').encode('utf-8')

            items = client.parseDOM(result, "item")

            for item in items:
                linkTitle = client.parseDOM(item, 'title')[0]

                try :
                    parsed = re.compile('(.+?) \((\d{4})\) ').findall(linkTitle)[0]
                    parsedTitle = parsed[0]
                    parsedYears = parsed[1]
                except:
                    parsedTitle = ''
                    pass

                if cleanedTitle == cleantitle.get(parsedTitle):
                    url = client.parseDOM(item, "link")[0]
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

            #url = urlparse.urljoin(self.base_link, url)

            try: result = client.request(url, referer=self.base_link)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.replace('\n','').replace('\t','')

            result = client.parseDOM(result, "div", attrs={"class": "entry-content clearfix single-post-content"})
            result = client.parseDOM(result, "p", attrs={"style":"text-align: center;"})
            items = client.parseDOM(result, "a", ret="href")

            for item in items:
                try :
                    url = item
                    if 'digibolly.se' in url :
                        result = client.request(url)
                        url = re.findall('<iframe src="(.+?)"',result, re.IGNORECASE)[0]
                    host = client.host(url)
                    srcs.append({'source': host, 'parts' : '1', 'quality': 'HD', 'scraper': self.name, 'url': url, 'direct':False})
                except :
                    pass
            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            return srcs