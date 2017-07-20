import re
import urllib
import BeautifulSoup

from aftershock.common import client, logger
from ..scraper import Scraper


class DesiPlex(Scraper):
    domains = ['desiplex.me']
    name = "desiplex"

    def __init__(self):
        self.base_link = 'http://www.desiplex.me'
        self.search_link = '/feed/?s=%s&submit=Search'
        self.info_link = '%s/watch/?id=%s'
        self.srcs = []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            query = '%s %s' % (title, episode)
            query = self.search_link % (urllib.quote_plus(query))

            result = client.request(self.base_link + query)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','').replace('\t','')

            items = client.parseDOM(result, 'content:encoded')[0]

            items = re.compile('class=\"single-heading\">(.+?)<span').findall(items)

            for i in range(0, len(items)):
                try :
                    if '720p' in items[i]:
                        quality = 'HD'
                    else:
                        quality = 'SD'

                    urls = client.parseDOM(items[i], "a", ret="href")
                    for j in range(0,len(urls)):

                        result = client.request(urls[j])

                        item = BeautifulSoup.BeautifulSoup(result, parseOnlyThese=BeautifulSoup.SoupStrainer("iframe"))

                        if len(item) == 0:
                            item = re.compile('data-config="(.+?)"').findall(result)[0]
                            item = [{"src":item}]

                        for links in item:
                            rUrl = links["src"]

                            if rUrl.startswith('//'):
                                rUrl='http:%s'%rUrl

                            urls[j] = rUrl
                            host = client.host(urls[0])
                    url = "##".join(urls)

                    self.srcs.append({'source':host, 'parts': str(len(urls)), 'quality':quality,'scraper':self.name,'url':url, 'direct':False})
                    urls = []
                except:
                    pass
            return self.srcs
        except:
            return self.srcs