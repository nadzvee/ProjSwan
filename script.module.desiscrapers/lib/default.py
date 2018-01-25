import sys

sys.argv = ['script.module.desiscrapers', '1']

import desiscrapers
import xbmcgui
import os
import xbmc
import xbmcaddon
import random
import xbmcvfs
from BeautifulSoup import BeautifulStoneSoup

from aftershock.common import control
try:
    from sqlite3 import dbapi2 as database
except:
    from pysqlite2 import dbapi2 as database


from aftershock.common import cleantitle, logger, control

movies = [
    {
        'title': 'Baadshaho',
        'imdb': '',
        'year': '2017'
    },
    {
        'title': 'Befikre',
        'imdb': 'tt00000000',
        'year': '2016'
    },
    {
        'title': 'Prem Ratan Dhan Payo',
        'imdb': 'tt3595298',
        'year': '2015'
    },
    {
        'title': 'Rustom',
        'imdb': 'tt5165344',
        'year': '2016'
    },
    {
        'title': 'Dangal',
        'imdb': 'tt5074352',
        'year': '2016'
    },
    {
        'title': 'Welcome Back',
        'imdb': 'tt3159708',
        'year': '2015'
    },
]

shows = [
    {
        'title': "Bigg Boss 11",
        'show_year': "",
        'year': "",
        'season': '',
        'episode': '8th October 2017',
        'imdb': 'threads/1085119-Bigg-Boss-Season-11-Weekend-Ka-Vaar-8th-October-2017-Watch-Online?s=6b53bae950baa63d1b4770050373e146',
    },
    {
        'title': "Yeh Rishta Kya Kehlata Hai",
        'show_year': "",
        'year': "",
        'season': '',
        'episode': '7th July 2017',
        'imdb': 'threads/1058940-Yeh-Rishta-Kya-Kehlata-Hai-27th-June-2017-Watch-Online',
    },
    {
        'title': "The Flash",
        'show_year': "2014",
        'year': "2016",
        'season': '3',
        'episode': '8',
        'imdb': 'tt3107288',
    },

]


def main():
    test_type = control.dialog.select("Choose type of test", ["Test List", "Profile List", "Profile Scrapers"])
    basepath = xbmc.translatePath(control.addonInfo("profile"))
    control.makeFile(basepath)
    if test_type == 0:
        test()
    elif test_type == 1:
        import cProfile
        cProfile.run('test()',
                     os.path.join(basepath, 'profile_list.profile'))
    elif test_type == 2:
        import cProfile
        cProfile.run('profile_scrapers("movie")',
                     os.path.join(basepath, 'profile_scrapers_movies.profile'))
        cProfile.run('profile_scrapers("episode")',
                     os.path.join(basepath, 'profile_scrapers_episodes.profile'))
    testManual()

def testManual():
    desiscrapers.clear_cache()
    try:
        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()
    except:
        logger.debug("Desiscrapers Testing Mode", 'Error connecting to db')
        sys.exit()

    testManualMovies()
    #testManualShows()

def testManualMovies():
    num_movies = len(movies)
    if num_movies > 0:
        logger.debug('Desiscrapers Testing mode active', 'please wait')
        index = 0
        for movie in movies:
            index += 1
            title = movie['title']
            year = movie['year']
            imdb = movie['imdb']
            logger.debug(" Scraping movie {} of {}".format(index, num_movies))
            links_scraper = desiscrapers.scrape_movie(title, year, imdb, host=['yomovies'])
            links_scraper = links_scraper()
            for scraper_links in links_scraper:
                if scraper_links:
                    random.shuffle(scraper_links)

def testManualShows():
    num_shows = len(shows)
    if num_shows > 0:
        index = 0
        for show in shows:
            index += 1
            title = show['title']
            show_year = show['show_year']
            year = show['year']
            season = show['season']
            episode = show['episode']
            imdb = show['imdb']
            tvdb = show.get('tvdb', '')

            links_scraper = desiscrapers.scrape_episode(title, show_year, year, season, episode, imdb, tvdb, host=['yodesi', 'badtameezdil'])
            links_scraper = links_scraper()
            for scraper_links in links_scraper:
                if scraper_links:
                    random.shuffle(scraper_links)


def test():
    global movies, shows
    try:
        test_movies = []
        test_episodes = []
        profile_path = xbmc.translatePath(control.addonInfo('profile')).decode('utf-8')
        test_file = xbmcvfs.File(os.path.join(profile_path, "testings.xml"))
        xml = BeautifulStoneSoup(test_file.read())
        test_file.close()
        items = xml.findAll("item")
        for item in items:
            try:
                content = item.find("content")
                if content:
                    if "movie" in content.text:
                        meta = item.find("meta")
                        test_movies.append({
                            'title': meta.find("title").text,
                            'imdb': meta.find("imdb").text,
                            'year': meta.find("year").text,
                        })
                    elif "episode" in content.text:
                        meta = item.find("meta")
                        test_episodes.append({
                            'title': meta.find("tvshowtitle").text,
                            'show_year': int(meta.find("premiered").text[0:4]),
                            'year': meta.find("year").text,
                            'season': meta.find("season").text,
                            'episode': meta.find("season").text,
                            'imdb': meta.find("imdb").text,
                        })
            except:
                pass

            movies = test_movies
            shows = test_episodes
    except:
        pass

    dialog = xbmcgui.Dialog()
    pDialog = xbmcgui.DialogProgress()
    if dialog.yesno("Desiscrapers Testing Mode", 'Clear cache?'):
        desiscrapers.clear_cache()
    try:
        dbcon = database.connect(control.cacheFile)
        dbcur = dbcon.cursor()
    except:
        dialog.ok("Desiscrapers Testing Mode", 'Error connecting to db')
        sys.exit()

    num_movies = len(movies)
    if num_movies > 0:
        pDialog.create('Desiscrapers Testing mode active', 'please wait')
        index = 0
        for movie in movies:
            index += 1
            title = movie['title']
            year = movie['year']
            imdb = movie['imdb']
            if pDialog.iscanceled():
                pDialog.close()
                break
            pDialog.update((index / num_movies) * 100, "Scraping movie {} of {}".format(index, num_movies), title)
            links_scraper = desiscrapers.scrape_movie(title, year, imdb)
            links_scraper = links_scraper()
            for scraper_links in links_scraper:
                if pDialog.iscanceled():
                    break
                if scraper_links:
                    logger.debug(scraper_links, __name__)
                    random.shuffle(scraper_links)

        pDialog.close()
        dbcur.execute("SELECT COUNT(DISTINCT(scraper)) FROM rel_src where episode = ''")
        match = dbcur.fetchone()
        num_movie_scrapers = match[0]

        logger.debug('num_movie_scrapers %s' % num_movie_scrapers, __name__)

        dbcur.execute("SELECT scraper, count(distinct(urls)) FROM rel_src where episode = '' group by scraper")
        matches = dbcur.fetchall()
        failed = []
        for match in matches:
            if int(match[1]) <= 1:
                failed.append(match[0])

        if len(failed) > 0:
            failedstring = "Failed: {}".format(len(failed))
            for fail in failed:
                failedstring += "\n        - {}".format(str(fail))
        else:
            failedstring = "Failed: {}".format(len(failed))

        logger.debug('failedString %s' % failedstring, __name__)

        dbcur.execute("SELECT title, count(distinct(urls)) FROM rel_src where episode = '' group by title")
        matches = dbcur.fetchall()
        failed_movies = []
        for match in matches:
            if int(match[1]) <= 1:
                if int(match[1]) == 1:
                    dbcur.execute(
                        "SELECT scraper, urls FROM rel_src where episode == '' and title == '{}' group by scraper".format(
                            match[0]))
                    new_matches = dbcur.fetchall()
                    found = False
                    for new_match in new_matches:
                        if new_match[1] == "[]":
                            continue
                        else:
                            found = True
                    if not found:
                        failed_movies.append(match[0])
                else:
                    failed_movies.append(match[0])

        if len(failed_movies) > 0:
            failed_movie_string = "Failed movies: {}".format(len(failed_movies))
            for fail in failed_movies:
                for movie in movies:
                    if cleantitle.get(movie['title']).upper() == str(fail):
                        failed_movie_string += "\n        - {}".format(movie["title"])

        else:
            failed_movie_string = ""

    num_shows = len(shows)
    if num_shows > 0:
        pDialog.create('Desiscrapers Testing mode active', 'please wait')
        index = 0
        for show in shows:
            index += 1
            title = show['title']
            show_year = show['show_year']
            year = show['year']
            season = show['season']
            episode = show['episode']
            imdb = show['imdb']
            tvdb = show.get('tvdb', '')

            if pDialog.iscanceled():
                pDialog.close()
                break
            pDialog.update((index / num_shows) * 100, "Scraping show {} of {}".format(index, num_shows), title)
            links_scraper = desiscrapers.scrape_episode(title, show_year, year, season, episode, imdb, tvdb)
            links_scraper = links_scraper()
            for scraper_links in links_scraper:
                if pDialog.iscanceled():
                    break
                if scraper_links:
                    random.shuffle(scraper_links)

        pDialog.close()
        dbcur.execute("SELECT COUNT(DISTINCT(scraper)) FROM rel_src where episode != ''")
        match = dbcur.fetchone()
        num_show_scrapers = match[0]

        dbcur.execute("SELECT scraper, count(distinct(urls)) FROM rel_src where episode != '' group by scraper")
        matches = dbcur.fetchall()
        failed = []
        for match in matches:
            if int(match[1]) <= 1:
                if int(match[1]) == 1:
                    dbcur.execute(
                        "SELECT scraper, urls FROM rel_src where episode != '' and scraper == '{}' group by scraper".format(
                            match[0]))
                    match = dbcur.fetchone()
                    if match[1] == "[]":
                        failed.append(match[0])
                else:
                    failed.append(match[0])

        if len(failed) > 0:
            show_scraper_failedstring = "Failed: {}".format(len(failed))
            for fail in failed:
                show_scraper_failedstring += "\n        - {}".format(str(fail))
        else:
            show_scraper_failedstring = ""

        dbcur.execute("SELECT title, count(distinct(urls)) FROM rel_src where episode != '' group by title")
        matches = dbcur.fetchall()
        failed_shows = []
        for match in matches:
            if int(match[1]) <= 1:
                if int(match[1]) == 1:
                    dbcur.execute(
                        "SELECT scraper, urls FROM rel_src where episode != '' and title == '{}' group by scraper".format(
                            match[0]))
                    new_matches = dbcur.fetchall()
                    found = False
                    for new_match in new_matches:
                        if new_match[1] == "[]":
                            continue
                        else:
                            found = True
                    if not found:
                        failed_shows.append(match[0])
                else:
                    failed_shows.append(match[0])

        if len(failed_shows) > 0:
            failed_show_string = "Failed shows: {}".format(len(failed_shows))
            for fail in failed_shows:
                for show in shows:
                    if cleantitle.get(show['title']).upper() == str(fail):
                        failed_show_string += "\n        - {} S{}-E{}".format(show["title"], show["season"],
                                                                              show["episode"])

        else:
            failed_show_string = ""

    resultstring = 'Results:\n'
    if num_movies > 0:
        resultstring = resultstring + \
                       '    Movie Scrapers: {}\n' \
                       '    {}\n' \
                       '    {}\n'.format(num_movie_scrapers, failedstring, failed_movie_string)
    if num_shows > 0:
        resultstring = resultstring + \
                       '    Episode Scrapers: {}\n' \
                       '    {}\n' \
                       '    {}\n'.format(num_show_scrapers, show_scraper_failedstring, failed_show_string)

    dialog.textviewer("Desiscrapers Testing Mode", resultstring)


def profile_scrapers(profile_type):
    global movies, shows
    from desiscrapers.hl import HostedLink
    import random
    if profile_type == "movie":
        movieindex = 1
        num_movies = len(movies)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Desiscrapers Testing mode active', 'please wait')
        for movie in movies:
            if pDialog.iscanceled():
                pDialog.close()
                break
            title = movie['title']
            year = movie["year"]
            imdb = movie["imdb"]
            hl = HostedLink(title, year, imdb, None)
            scrapers = hl.get_scrapers()
            num_scrapers = len(scrapers)
            index = 1
            for scraper in scrapers:
                if pDialog.iscanceled():
                    pDialog.close()
                    break
                pDialog.update((index / num_scrapers) * 100,
                               "Scraping movie {} of {} with scraper {} of {}".format(movieindex, num_movies, index,
                                                                                      num_scrapers),
                               "current scraper: {}".format(scraper.name))
                scraper.scrape_movie(title, year, imdb)
                index += 1
            movieindex += 1
        pDialog.close()
    elif profile_type == "episode":
        episodeindex = 1
        num_episodes = len(movies)
        pDialog = xbmcgui.DialogProgress()
        pDialog.create('Desiscrapers Testing mode active', 'please wait')
        for show in shows:
            if pDialog.iscanceled():
                pDialog.close()
                break
            title = show['title']
            year = show["year"]
            imdb = show["imdb"]
            show_year = show["show_year"]
            season = show["season"]
            episode = show["episode"]
            hl = HostedLink(title, year, imdb, None)
            scrapers = hl.get_scrapers()
            num_scrapers = len(scrapers)
            index = 0
            for scraper in scrapers:
                if pDialog.iscanceled():
                    pDialog.close()
                    break
                pDialog.update((index / num_scrapers) * 100,
                               "Scraping episode {} of {} with scraper {} of {}".format(episodeindex, num_episodes,
                                                                                        index, num_scrapers),
                               "current scraper: {}".format(scraper.name))
                scraper.scrape_episode(title, show_year, year, season, episode, imdb, None)
                index += 1
            episodeindex +=1
        pDialog.close()


if __name__ == '__main__':
    desiscrapers._update_settings_xml()
    main()
