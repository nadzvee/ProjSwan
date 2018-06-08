import re
import urllib
import urlparse
import base64
import time
import json

from aftershock.common import cleantitle, client, logger, directstream
from ..scraper import Scraper


class PutLocker(Scraper):
    domains = ['putlocker.systems', 'putlocker-movies.tv', 'putlocker.yt', 'cartoonhd.website']
    name = "putlocker"
    userAgent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'

    def __init__(self):
        self.base_link = 'http://putlockerhd.co'
        self.srcs = []

    def scrape_movie(self, title, year, imdb, debrid = False):
        try:
            query = cleantitle.get(title)
            query = '/watch?v=%s_%s' % (query.replace(' ','_'),year)
            query = urlparse.urljoin(self.base_link, query)
            headers = {'User-Agent':self.userAgent}

            result = client.request(query, headers=headers)

            varid = re.compile('var frame_url = "(.+?)"',re.DOTALL).findall(result)[0].replace('/embed/','/streamdrive/info/')
            res_chk = re.compile('class="title"><h1>(.+?)</h1>',re.DOTALL).findall(result)[0]
            varid = 'http:'+varid
            holder = client.request(varid,headers=headers).content
            links = re.compile('"src":"(.+?)"',re.DOTALL).findall(holder)
            count = 0
            for link in links:
                link = link.replace('\\/redirect?url=','')
                link = urllib.unquote(link).decode('utf8')
                if '1080' in res_chk:
                    res= '1080p'
                elif '720' in res_chk:
                    res='720p'
                else:
                    res='DVD'
                count +=1
                self.srcs.append({'source': 'Googlelink','parts' : '1', 'quality': res,'scraper': self.name,'url':link,'direct': False})

            return self.srcs
        except Exception as e:
            logger.error('[%s] Exception : %s' % (self.__class__, e))
            pass
        return []

    def scrape_episode(self, title, show_year, year, season, episode, imdb, tvdb, debrid = False):
        try:
            url = {'tvshowtitle': title, 'season': season, 'episode': episode, 'imdb':imdb, 'tvdb':tvdb, 'year':year}
            url = urllib.urlencode(url)
            return self.sources(client.replaceHTMLCodes(url))
        except:
            pass
        return []

    def sources(self, url):
        logger.debug('SOURCES URL %s' % url, __name__)
        try:
            srcs = []

            if url == None: return srcs

            start_url = '%s/watch?v=%s_%s' %(self.base_link,search_id.replace(' ','_'),year)

            if not str(url).startswith('http'):

                data = urlparse.parse_qs(url)
                data = dict([(i, data[i][0]) if data[i] else (i, '') for i in data])

                title = data['tvshowtitle'] if 'tvshowtitle' in data else data['title']


                if 'tvshowtitle' in data:
                    url = '%s/tv-show/%s/season/%01d/episode/%01d' % (self.base_link, cleantitle.geturl(title), int(data['season']), int(data['episode']))
                else:
                    url = '%s/movie/%s' % (self.base_link, cleantitle.geturl(title))

                result = client.request(url, limit='5')
                result = client.parseDOM(result, 'title')[0]

                if '%TITLE%' in result: raise Exception()

                r = client.request(url, output='extended')


            else:
                url = urlparse.urljoin(self.base_link, url)

                r = client.request(url, output='extended')


            cookie = r[4] ; headers = r[3] ; result = r[0]

            try: auth = re.findall('__utmx=(.+)', cookie)[0].split(';')[0]
            except: auth = 'false'
            auth = 'Bearer %s' % urllib.unquote_plus(auth)

            headers['Authorization'] = auth
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Content-Type'] = 'application/x-www-form-urlencoded; charset=UTF-8'
            headers['Accept'] = 'application/json, text/javascript, */*; q=0.01'
            headers['Cookie'] = cookie
            headers['Referer'] = url


            u = '/ajax/tnembeds.php'
            self.base_link = client.request(self.base_link, output='geturl')
            u = urlparse.urljoin(self.base_link, u)

            action = 'getEpisodeEmb' if '/episode/' in url else 'getMovieEmb'

            elid = urllib.quote(base64.encodestring(str(int(time.time()))).strip())

            token = re.findall("var\s+tok\s*=\s*'([^']+)", result)[0]

            idEl = re.findall('elid\s*=\s*"([^"]+)', result)[0]

            post = {'action': action, 'idEl': idEl, 'token': token, 'elid': elid}
            post = urllib.urlencode(post)

            r = client.request(u, post=post, headers=headers)
            r = str(json.loads(r))
            r = client.parseDOM(r, 'iframe', ret='.+?') + client.parseDOM(r, 'IFRAME', ret='.+?')


            links = []

            for i in r:
                try: links += [{'source': 'gvideo', 'quality': directstream.googletag(i)[0]['quality'], 'url': i, 'direct': True}]
                except: pass

            links += [{'source': 'openload.co', 'quality': 'SD', 'url': i, 'direct': False} for i in r if 'openload.co' in i]


            for i in links: srcs.append({'source': i['source'], 'quality': i['quality'], 'scraper': self.name, 'url': i['url'], 'direct': i['direct']})

            logger.debug('SOURCES [%s]' % srcs, __name__)
            return srcs
        except:
            return srcs