import re
import urllib

from aftershock.common import client, logger
from ..scraper import Scraper


class BadtameezDil(Scraper):
    domains = ['badtameezdilnet.com/']
    name = "badtameezdil"

    def __init__(self):
        self.base_link = 'http://badtameezdilnet.com'
        self.search_link = '/feed/?s=%s'
        self.srcs = []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            query = '%s %s' % (title, episode)
            query = self.search_link % (urllib.quote_plus(query))

            try: result = client.request(self.base_link + query)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','').replace('\t','')

            result = client.parseDOM(result, 'content:encoded')[0]

            url = client.parseDOM(result, "a", attrs={"rel": "nofollow"}, ret="href")[0]

            if url == None:
                pass
            else:
                return self.sources(client.replaceHTMLCodes(url))
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
        return []

    def sources(self, url):
        try:
            logger.debug('SOURCES URL %s' % url, __name__)
            quality = 'HD'
            srcs = []

            try: result = client.request(url)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','').replace('\t','')

            result = client.parseDOM(result, "div", attrs={"class": "single-post-video"})[0]

            items = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(result)

            for item in items:
                if item[1].endswith('png'):
                    continue
                host = client.host(item[1])
                url = item[1]
                parts = [url]
            srcs.append({'source':host, 'parts': len(parts), 'quality':quality,'scraper':self.name,'url':"##".join(parts), 'direct':False})
            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs