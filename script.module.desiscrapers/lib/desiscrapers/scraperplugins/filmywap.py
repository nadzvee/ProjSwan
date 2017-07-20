import base64
import json
import re
import urllib, urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class FilmyWap(Scraper):
    domains = ['fimlywap.im.to','fimlywap.desi','filmywap.com']
    name = "filmywap"

    def __init__(self):
        self.base_link = 'http://fimlywap.desi'
        self.search_link = 'aHR0cHM6Ly93d3cuZ29vZ2xlYXBpcy5jb20vY3VzdG9tc2VhcmNoL3YxZWxlbWVudD9rZXk9QUl6YVN5Q1ZBWGlVelJZc01MMVB2NlJ3U0cxZ3VubU1pa1R6UXFZJnJzej1maWx0ZXJlZF9jc2UmbnVtPTEwJmhsPWVuJmN4PTAwNjE2OTI4MDMzMzcxNDY1MDkyNzotMGVwYXI3djBqeSZnb29nbGVob3N0PXd3dy5nb29nbGUuY29tJnE9JXM='
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            t = cleantitle.get(title)

            try:
                query = '%s %s' % (title, year)
                query = base64.b64decode(self.search_link) % urllib.quote_plus(query)

                result = client.request(query)
                result = json.loads(result)['results']
                r = [(i['url'], i['titleNoFormatting']) for i in result]
                r = [(i[0], re.compile('(.+?) [\d{4}|(\d{4})]').findall(i[1])) for i in r]
                r = [(i[0], i[1][0]) for i in r if len(i[1]) > 0]
                r = [x for y,x in enumerate(r) if x not in r[:y]]
                r = [i for i in r if t == cleantitle.get(i[1])]
                u = [i[0] for i in r][0]

            except:
                return

            url = u
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
            srcs = []

            if url == None: return srcs

            result, response_code, response_headers, headers, cookie = client.request(url, output='extended')

            result = result.replace('\n','').replace('\t','').replace('\r','')
            referer = headers.get('Referer')
            result = client.parseDOM(result, 'div', attrs={"class":"detail ls_item"})[0]

            link = client.parseDOM(result, 'div', attrs={"class":"loaer_detai"})[0]
            link = client.parseDOM(link, 'a', ret='href')[0]

            link = urlparse.urljoin(referer, link)

            result = client.request(link)
            result = client.parseDOM(result, 'div', attrs={"class":"video-container"})[0]
            url = client.parseDOM(result, 'iframe', ret='src')[0]

            host = client.host(url)

            srcs.append({'source': host, 'parts' : '1', 'quality': 'HD', 'scraper': self.name, 'url': url, 'direct': False})

            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except :
            return srcs