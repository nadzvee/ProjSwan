import re
import urllib

from aftershock.common import client, logger, cleantitle
from ..scraper import Scraper


class DesiTashan(Scraper):
    domains = ['desiserials.org']
    name = "desiserials"

    def __init__(self):
        self.base_link = 'http://www.desiserials.org'
        self.search_link = '/feed/?s=%s&submit=Search'
        self.srcs = []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:

            query = '%s %s' % (title, episode)
            query = self.search_link % (urllib.quote_plus(query))

            result = client.request(self.base_link + query)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','').replace('\t','')

            items = client.parseDOM(result, 'item')

            cleanedTitle = cleantitle.get('%s %s' % (title, episode))

            for item in items:
                linkTitle = client.parseDOM(item, 'title')[0]
                linkTitle = cleantitle.get(linkTitle).replace('watchonlineepisodehd','')
                if cleanedTitle == linkTitle :
                    url = client.parseDOM(item, "link")[0]
                    break

            return self.sources(client.replaceHTMLCodes(url))
        except:
            return self.srcs

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            quality = ''
            srcs = []

            if url == None: return srcs

            result = client.request(url)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','')

            result = client.parseDOM(result, "div", attrs={"class": "post-content bottom"})[0]

            items = client.parseDOM(result, "p")

            hosts = client.parseDOM(result, "span", attrs={"style":"color: red;"})

            links = []

            for item in items:
                if 'a href' in item:
                    links.append(item)
            items = zip(hosts, links)

            for item in items:
                self.srcs.extend(self.source(item))

            logger.debug('SOURCES [%s]' % self.srcs, __name__)
            return self.srcs
        except Exception as e:
            logger.error(e)
            return self.srcs

    def source(self, item):

        title = item[0]
        links = item[1]
        urls = []
        if '720p' in title:
            quality = 'HD'
        else:
            quality = 'SD'

        parts = client.parseDOM(links, "a", ret="href")
        srcs = []

        for part in parts:
            try :
                part = client.request(part)
                part = part.decode('iso-8859-1').encode('utf-8')
                part = client.parseDOM(part, "td", attrs={"style":"vertical-align:middle;text-align:center;"})[0]
                tUrl = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(part)[0][1]
                host = client.host(tUrl)
                urls.append(tUrl)

            except Exception as e:
                logger.error(e)
                pass

        url = "##".join(urls)
        srcs.append({'source': host, 'parts': len(urls), 'quality': quality, 'scraper': self.name, 'url': url, 'direct':False})

        return srcs