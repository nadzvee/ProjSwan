import re
import urllib

from aftershock.common import client, logger, cleantitle
from ..scraper import Scraper


class FifaStop(Scraper):
    domains = ['fifastop.com']
    name = "fifastop"

    def __init__(self):
        self.base_link = 'http://www.fifastop.com'
        self.search_link = '/search.php?keywords=%s'
        self.srcs = []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:

            query = '%s %s' % (title, episode)
            cleanedTitle = cleantitle.get(query)
            query = self.search_link % (urllib.quote_plus(query))

            try: result = client.request(self.base_link + query)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','').replace('\t','')

            items = client.parseDOM(result, "div", attrs={"class":"pm-li-video"})

            for item in items:
                item = client.parseDOM(item, "h3")[0]
                sUrl = client.parseDOM(item, "a", ret="href")[0]
                linkTitle = client.parseDOM(item, "a", ret="title")[0]
                if cleanedTitle == cleantitle.get(linkTitle) :
                    url = sUrl
                    break

            quality = 'HD'
            host = client.host(url)
            self.srcs.append({'source':host, 'parts': '1', 'quality':quality,'scraper':self.name,'url':url, 'direct':False})
            return self.srcs
        except:
            return self.srcs