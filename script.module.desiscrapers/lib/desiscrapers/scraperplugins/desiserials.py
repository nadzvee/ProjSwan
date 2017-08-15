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
                    self.srcs.extend(self.source(item))
            return self.srcs
        except:
            return self.srcs

    def source(self, item):
        try:
            srcs = []

            links = client.parseDOM(item, 'link')

            for link in links:

                if 'span' in link:
                    if 'HD' in link:
                        quality = 'HD'
                    else:
                        quality = 'SD'
                    continue

                urls = client.parseDOM(link, 'a', ret='href')

                if len(urls) > 0 :

                    for i in range(0, len(urls)) :
                        urls[i] = client.urlRewrite(urls[i])

                    host = client.host(urls[0])
                    url = "##".join(urls)

                    srcs.append({'source':host, 'parts': str(len(urls)), 'quality':quality,'scraper':self.name,'url':url, 'direct':False})
                    urls = []
            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            pass