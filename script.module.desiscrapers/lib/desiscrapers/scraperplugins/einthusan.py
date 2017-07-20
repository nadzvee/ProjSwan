import re
import urllib, urllib2
import urlparse, gzip, StringIO

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class Einthusan(Scraper):
    domains = ['einthusan.com', 'einthusan.tv']
    name = "einthusan"

    def __init__(self):

        self.priority = 1
        self.language = ['en']
        self.base_link = 'https://einthusan.tv'
        self.search_link = '/movie/results/?lang=%s&query=%s'
        self.movie_link = '/movie/watch/%s/'

        self.srcs = []

    def request(self, url):
        try:
            req = urllib2.Request(url)
            req.add_header('User-Agent', client.randomagent())
            res = urllib2.urlopen(req)
            r = res.read() if not res.info().getheader('Content-Encoding') == 'gzip' else gzip.GzipFile(fileobj=StringIO.StringIO(res.read())).read()
            res.close()
            return r
        except:
            return

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            langMap = {'hi':'hindi', 'ta':'tamil', 'te':'telugu', 'ml':'malayalam', 'kn':'kannada', 'bn':'bengali', 'mr':'marathi', 'pa':'punjabi'}

            lang = 'http://www.imdb.com/title/%s/' % imdb
            lang = client.request(lang)
            lang = re.findall('href\s*=\s*[\'|\"](.+?)[\'|\"]', lang)
            lang = [i for i in lang if 'primary_language' in i]
            lang = [urlparse.parse_qs(urlparse.urlparse(i).query) for i in lang]
            lang = [i['primary_language'] for i in lang if 'primary_language' in i]
            lang = langMap[lang[0][0]]

            q = self.search_link % (lang, urllib.quote_plus(title))
            q = urlparse.urljoin(self.base_link, q)

            t = cleantitle.get(title)

            r = self.request(q)

            r = client.parseDOM(r, 'li')
            r = [(client.parseDOM(i, 'a', ret='href'), client.parseDOM(i, 'h3'), client.parseDOM(i, 'div', attrs = {'class': 'info'})) for i in r]
            r = [(i[0][0], i[1][0], i[2][0]) for i in r if i[0] and i[1] and i[2]]
            r = [(re.findall('(\d+)', i[0]), i[1], re.findall('(\d{4})', i[2])) for i in r]
            r = [(i[0][0], i[1], i[2][0]) for i in r if i[0] and i[2]]
            r = [i[0] for i in r if t == cleantitle.get(i[1]) and year == i[2]][0]

            url = str(r)
            return self.sources(client.replaceHTMLCodes(url))
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass

        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            sources = []

            if url == None: return sources

            url = self.movie_link % url
            url = urlparse.urljoin(self.base_link, url)

            r = self.request(url)

            sources.append({'source': 'einthusan', 'quality': 'HD', 'scraper':self.name,'url': url, 'direct': True, 'debridonly': False})
            logger.debug('SOURCES URL %s' % url, __name__)
        except:
            pass

        return sources