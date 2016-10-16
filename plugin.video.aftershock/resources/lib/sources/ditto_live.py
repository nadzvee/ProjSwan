# -*- coding: utf-8 -*-

'''
    Aftershock Add-on
    Copyright (C) 2015 IDev

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''


import json, urlparse, re, urllib, os
from resources.lib.libraries import client
from resources.lib.libraries import cleantitle
from resources.lib.libraries import logger
from resources.lib.libraries import pyaes
from resources.lib.libraries import control
from resources.lib.libraries.fileFetcher import *
from resources.lib.libraries.liveParser import *

class source:
    def __init__(self):
        self.base_link = 'http://www.dittotv.com'
        self.live_link = 'http://origin.dittotv.com/livetv/all/0'
        self.channel_link = 'http://origin.dittotv.com%s'
        self.poster_link = 'http://dittotv2.streamark.netdna-cdn.com/vod_images/optimized/livetv/%s.jpg'
        self.headers = {'Accept':'text/html,application/xhtml+xml,q=0.9,image/jxr,*/*',
                        'Accept-Language':'en-US,en;q=0.5',
                        'Accept-Encoding':'gzip, deflate',
                        'Connection':'keep-alive',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0' ,
                        'Referer':'http://www.dittotv.com/livetv'}
        self.list = []
        self.fileName = 'ditto.json'

    def getLiveSource(self, generateJSON=False):
        try :

            if generateJSON:
                url = self.live_link

                #result = client.source(url, headers=self.headers)
                fileName = os.path.join(control.dataPath, 'ditto.html')
                #file = open(fileName, "w")
                #file.write(result)
                file = open(fileName, "r")
                result = file.read()
                #result = result.decode('iso-8859-1').encode('utf-8')
                #result = result.replace('\n','').replace('\t','')
                channels=re.findall('<div class="subpattern.*?\s*<a href="(.*?)" title="(.*?)".*?\s*<img src=".*?".*?\s*<img src="(.*?)"',result)

                channelList = {}
                for url, title, logo in channels:
                    title = title.replace("&amp;","And")
                    title = cleantitle.live(title)
                    title = title.title()
                    if 'temple' in title.lower():
                        continue
                    url = self.channel_link % url
                    poster = self.poster_link % str(logo)
                    channelList[title] ={'icon':poster,'url':url,'provider':'ditto','source':'ditto','direct':'false', 'quality':'HD', 'enabled':'true'}

                filePath = os.path.join(control.dataPath, self.fileName)
                with open(filePath, 'w') as outfile:
                    json.dump(channelList, outfile)

            fileFetcher = FileFetcher(self.fileName,control.addon)
            if fileFetcher.fetchFile() < 0:
                raise Exception()

            liveParser = LiveParser(self.fileName, control.addon)
            self.list = liveParser.parseFile()
            return self.list
        except:
            import traceback
            traceback.print_exc()
            pass

    def resolve(self, url, resolverList):
        try :
            logger.debug('ORIGINAL URL [%s]' % url, __name__)
            result = client.source(url, headers=self.headers)
            playdata='window.pl_data = (\{.*?"key":.*?\}\})'
            result=re.findall(playdata, result)[0]
            try :
                result = json.loads(result)
                link = result['live']['channel_list'][0]['file']
                key = result['live']['key']
                link = link.decode('base64')
                key = key.decode('base64')

                de = pyaes.new(key, pyaes.MODE_CBC, IV='\0'*16)
                link = de.decrypt(link).replace('\x00', '').split('\0')[0]
                link = re.sub('[^\s!-~]', '', link)
            except:link = client.parseDOM(result, "source", attrs={"type":"application/x-mpegurl"}, ret="src")[0]
            url = '%s|Referer=%s' % (link, url)
            logger.debug('RESOLVED URL [%s]' % url, __name__)
            return url
        except :
            return False