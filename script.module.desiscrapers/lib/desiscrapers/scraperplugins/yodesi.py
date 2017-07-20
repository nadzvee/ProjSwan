import re
import urllib

from aftershock.common import client, logger
from ..scraper import Scraper


class YoDesi(Scraper):
    domains = ['badtameezdil.net']
    name = "yodesi"

    def __init__(self):
        self.base_link = 'http://www.yodesi.net'
        self.search_link = '/feed/?s=%s&submit=Search'
        self.info_link = 'http://www.yo-desi.com/player.php?id=%s'
        self.srcs = []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            query = '%s %s' % (title, episode)
            query = self.search_link % (urllib.quote_plus(query))

            try: result = client.request(self.base_link + query)
            except: result = ''

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','').replace('\t','')

            items = client.parseDOM(result, 'content:encoded')[0]

            items = re.compile('class=\"single-heading\">(.+?)<span').findall(items)

            for i in range(0, len(items)):
                self.source(items[i])
        except:
            return self.srcs

    def source(self, item):
        try:
            try :
                if '720p' in item:
                    quality = 'HD'
                else:
                    quality = 'SD'

                urls = client.parseDOM(item, "a", ret="href")

                for j in range(0,len(urls)):
                    videoID = self.getVideoID(urls[j])

                    result = client.request(self.info_link % videoID)

                    result = result.decode('iso-8859-1').encode('utf-8')

                    item = client.parseDOM(result, name="div", attrs={"style": "float:none;height:700px;margin-left:200px"})[0]

                    rUrl = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(item)[0][1]

                    if not rUrl.startswith('http:') and not rUrl.startswith('https:'):
                        rUrl = '%s%s' % ('http:', rUrl)

                    urls[j] = rUrl

                host = client.host(urls[0])
                url = "##".join(urls)

                self.srcs.append({'source':host, 'parts': str(len(urls)), 'quality':quality, 'scraper':self.name, 'url':url, 'direct':False})
                urls = []
            except Exception as e:
                logger.error(e)
                pass
        except:
            return self.srcs

    def getVideoID(self, url):
        try :
            return re.compile('(id|url|v|si|sim|data-config)=(.+?)/').findall(url + '/')[0][1]
        except:
            return