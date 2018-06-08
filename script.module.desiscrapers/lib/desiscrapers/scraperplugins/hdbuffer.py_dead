import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class HDBuffer(Scraper):
    domains = ['hdbuffer.com']
    name = "hdbuffer"

    def __init__(self):

        self.base_link = 'http://hdbuffer.com'
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
            result = client.parseDOM(result, "item")

            cleanedTitle = cleantitle.get(title)

            for item in result:
                linkTitle = client.parseDOM(item, "title")[0]
                try :
                    parsed = re.compile('(.+?) [\(](\d{4})[\)]').findall(linkTitle)[0]
                    parsedTitle = parsed[0]
                    parsedYear = parsed[1]
                except:
                    pass

                if cleanedTitle == cleantitle.get(parsedTitle) and year == parsedYear:
                    url = client.parseDOM(item, "link")[0]
                    break

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

            result = client.request(url)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','')

            categories = client.parseDOM(result, "div", attrs={"id": "extras"})
            categories = client.parseDOM(categories, "a", attrs={"rel": "category tag"})

            for category in categories:
                category = category.lower()
                if "scr" in category:
                    quality = "SCR"
                    break
                elif "bluray" in category:
                    quality = "HD"
                    break

            links = client.parseDOM(result, "div", attrs={"class": "GTTabs_divs GTTabs_curr_div"})
            links += client.parseDOM(result, "div", attrs={"class": "GTTabs_divs"})

            for link in links:
                try :
                    url = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(link)[0][1]
                    host = client.host(url)

                    srcs.append({'source': host, 'parts': '1', 'quality': quality, 'scraper': self.name, 'url': url, 'direct':False})
                except :
                    pass

            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs