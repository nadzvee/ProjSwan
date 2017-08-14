import re
import urllib

from aftershock.common import client, logger, cleantitle, cache
from ..scraper import Scraper


class DesiRulez(Scraper):
    domains = ['desirulez.net', 'desirulez.me']
    name = "desirulez"

    def __init__(self):
        self.base_link = 'http://www.desirulez.net'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            movies = cache.get(self.desiRulezCache, 168)
            url = [i['url'] for i in movies if cleantitle.get(i['title'].decode('UTF-8')) == cleantitle.get(title)]
            return self.sources(client.replaceHTMLCodes(url))
        except Exception as e:
            logger.error(e)
            pass
        return []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            return self.sources(client.replaceHTMLCodes(imdb))
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            srcs = []

            result = client.request(self.base_link + '/' + url)

            result = result.decode('iso-8859-1').encode('utf-8')

            result = result.replace('\n','')

            ### DIRTY Implementation
            import BeautifulSoup
            soup = BeautifulSoup.BeautifulSoup(result).findAll('blockquote', {'class':re.compile(r'\bpostcontent\b')})[0]

            for e in soup.findAll('br'):
                e.extract()
            if soup.has_key('div'):
                soup = soup.findChild('div', recursive=False)
            urls = []
            quality = ''
            for child in soup.findChildren():
                if (child.getText() == '') or ((child.name == 'font' or child.name == 'a') and re.search('DesiRulez', str(child.getText()),re.IGNORECASE)):
                    continue
                elif (child.name == 'font') and re.search('Links|Online|Link',str(child.getText()),re.IGNORECASE):
                    if len(urls) > 0:
                        for i in range(0,len(urls)):
                            try :
                                result = client.request(urls[i])
                                item = client.parseDOM(result, name="div", attrs={"style": "float:right;margin-bottom:10px"})[0]
                                rUrl = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(item)[0][1]
                                rUrl = client.urlRewrite(rUrl)
                                urls[i] = rUrl
                            except :
                                urls[i] = client.urlRewrite(urls[i])
                                pass
                        host = client.host(urls[0])
                        url = "##".join(urls)
                        srcs.append({'source':host, 'parts': str(len(urls)), 'quality':quality,'provider':'DesiRulez','url':url, 'direct':False})
                        quality = ''
                        urls = []
                    quality = child.getText()
                    if '720p HD' in quality:
                        quality = 'HD'
                    elif 'Scr' in quality :
                        quality = 'SCR'
                    else :
                        quality = ''
                elif (child.name =='a') and not child.getText() == 'registration':
                    urls.append(str(child['href']))
                    if quality == '' :
                        quality = child.getText()
                        if '720p HD' in quality:
                            quality = 'HD'
                        elif 'Scr' in quality :
                            quality = 'SCR'
                        elif 'Dvd' in quality :
                            quality = 'SD'
                        else :
                            quality = ''

            if len(urls) > 0:
                for i in range(0,len(urls)):
                    try :
                        result = client.request(urls[i])
                        item = client.parseDOM(result, name="div", attrs={"style": "float:right;margin-bottom:10px"})[0]
                        rUrl = re.compile('(SRC|src|data-config)=[\'|\"](.+?)[\'|\"]').findall(item)[0][1]
                        rUrl = client.urlRewrite(rUrl)
                        urls[i] = rUrl
                    except :
                        urls[i] = client.urlRewrite(urls[i])
                        pass
                host = client.host(urls[0])
                url = "##".join(urls)
                srcs.append({'source': host, 'parts' : str(len(urls)), 'quality': quality, 'scraper': self.name, 'url': url,'direct':False})
            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs

    def desiRulezCache(self):
        try :
            base_link = 'http://www.desirulez.me/forums/20-Latest-Exclusive-Movie-HQ'
            result = client.request(base_link)
            result = result.decode('iso-8859-1').encode('utf-8')
            result = client.parseDOM(result, "li", attrs = {"class": "threadbit hot"})
            movies = []
            for link in result:
                link = client.parseDOM(link, "h3", attrs={"class": "threadtitle"})[0]
                url = client.parseDOM(link, "a", ret="href")[0]
                linkTitle = client.parseDOM(link, "a")[0]
                parsed = re.compile('(.+) [\(](\d{4})[/)] ').findall(linkTitle)[0]
                title = parsed[0].encode('ascii', 'ignore')
                year = parsed[1]
                movies.append({'url':url, 'title':title, 'year':year})
            return movies
        except:
            import traceback
            traceback.print_exc()
            pass