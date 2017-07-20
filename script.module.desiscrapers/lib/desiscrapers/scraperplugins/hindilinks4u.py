import re
import urllib
import urlparse

from aftershock.common import cleantitle, client, logger
from ..scraper import Scraper


class HindiLinks4U(Scraper):
    domains = ['hindilinks4u.to']
    name = "hindilinks4u"

    def __init__(self):
        self.base_link = 'https://www.hindilinks4u.to'
        self.search_link = '/feed/?s=%s&submit=Search'
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

                if cleanedTitle == cleantitle.get(linkTitle):
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
            srcs = []

            if url == None: return srcs

            result = client.request(url)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','')

            result = client.parseDOM(result, name="div", attrs={"class" : "entry-content rich-content"})[0]
            result = client.parseDOM(result, name="p")
            try :
                quality = host = ''
                urls = []

                result = result[1::]
                serversList = result[::2]
                linksList = result[1::2]

                for i in range(0, len(serversList)):
                    try :
                        links = linksList[i]
                        urls = client.parseDOM(links, name="a", ret="href")

                        for j in range(0, len(urls)):
                            try :
                                item = client.request(urls[j], mobile=True)
                                item = client.parseDOM(item, "td")[0]
                                item = re.compile('(SRC|src|data-config)=\"(.+?)\"').findall(item)[0][1]
                                urls[j] = item
                            except:
                                pass

                        if len(urls) > 1:
                            url = "##".join(urls)
                        else:
                            url = urls[0]

                        host = client.host(urls[0])

                        srcs.append({'source': host, 'parts': str(len(urls)), 'quality': quality, 'scraper': self.name, 'url': url, 'direct':False})
                    except:
                        pass
            except:
                pass

            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs