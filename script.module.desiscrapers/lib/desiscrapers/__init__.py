import os
from hl import HostedLink
from scraper import Scraper
from scraperplugins import *

from aftershock.common import control


def scrape_movie(title, year, imdb, host=None, include_disabled=False, timeout=30, exclude=None, enable_debrid = False):
    return HostedLink(title, year, imdb, None, host, include_disabled, timeout, exclude, enable_debrid, scraper_type='movie').scrape_movie()


def scrape_movie_with_dialog(title, year, imdb, host=None, include_disabled=False, timeout=30, exclude=None,
                             sort_function=None, check_url=False, extended=False, enable_debrid = False):
    return HostedLink(title, year, imdb, None, host, include_disabled, timeout, exclude, enable_debrid, scraper_type='movie').scrape_movie_with_dialog(
        sort_function=sort_function, check_url=check_url, extended=extended)


def scrape_episode(title, show_year, year, season, episode, imdb, tvdb, host=None, include_disabled=False, timeout=30,
                   exclude=None, enable_debrid = False):
    return HostedLink(title, year, imdb, tvdb, host, include_disabled, timeout, exclude, enable_debrid, scraper_type='episode').scrape_episode(show_year,
                                                                                                        season,
                                                                                                        episode)

def scrape_episode_with_dialog(title, show_year, year, season, episode, imdb, tvdb, host=None, include_disabled=False,
                               timeout=30, exclude=None, sort_function=None, check_url=False, extended=False, enable_debrid = False):
    return HostedLink(title, year, imdb, tvdb, host, include_disabled, timeout, exclude, enable_debrid, scraper_type='episode').scrape_episode_with_dialog(
        show_year,
        season,
        episode, sort_function=sort_function, check_url=check_url, extended=extended)


def scrape_song(title, artist, host=None, include_disabled=False, timeout=30, exclude=None, enable_debrid = False):
    return HostedLink(title, None, None, None, host, include_disabled, timeout, exclude, enable_debrid).scrape_song(title, artist)


def scrape_song_with_dialog(title, artist, host=None, include_disabled=False, timeout=30, exclude=None,
                            sort_function=None, extended=False, enable_debrid = False):
    return HostedLink(title, None, None, None, host, include_disabled, timeout, exclude, enable_debrid).scrape_song_with_dialog(title,
                                                                                                                 artist,
                                                                                                                 sort_function=sort_function,
                                                                                                                 extended=extended)


def relevant_scrapers(names_list=None, include_disabled=False, exclude=None, scraper_type=None):
    if exclude is None:
        exclude = []
    if names_list is None:
        names_list = ["ALL"]
    if type(names_list) is not list:
        names_list = [names_list]

    classes = Scraper.__class__.__subclasses__(Scraper)

    if scraper_type == None:
        classes = [(i, '1') for i in classes]
    elif scraper_type == 'movie':
        classes = [(i, getattr(i, 'scrape_movie', None)) for i in classes]
    elif scraper_type == 'episode':
        classes = [(i, getattr(i, 'scrape_episode', None)) for i in classes]

    classes = [i[0] for i in classes if not i[1] == None]
    relevant = []

    for index, domain in enumerate(names_list):
        if isinstance(domain, basestring) and not domain == "ALL":
            names_list[index] = domain.lower()

    for scraper in classes:
        if include_disabled or scraper._is_enabled():
            if names_list == ["ALL"] or (
                    any(name in scraper.name.lower() for name in names_list)):
                if not any(name.lower() == scraper.name.lower() for name in exclude):
                    relevant.append(scraper)
    return relevant


def clear_cache():
    try:
        from sqlite3 import dbapi2 as database
    except:
        from pysqlite2 import dbapi2 as database

    cache_location = control.cacheFile

    dbcon = database.connect(cache_location)
    dbcur = dbcon.cursor()

    try:
        dbcur.execute("DROP TABLE IF EXISTS rel_src")
        dbcur.execute("DROP TABLE IF EXISTS rel_music_src")
        dbcur.execute("VACUUM")
        dbcon.commit()
    except:
        pass


def _update_settings_xml():
    settings_location = os.path.join(control.addonInfo('path'), 'resources',
                                     'settings.xml')
    try:
        os.makedirs(os.path.dirname(settings_location))
    except OSError:
        pass

    new_xml = [
        '<?xml version="1.0" encoding="utf-8" standalone="yes"?>',
        '<settings>',
        '\t <category label = "General">',
        '\t\t<setting id="cache_enabled" ''type="bool" label="Enable Caching" default="true"/>',
        '\t\t<setting id="debug" ''type="bool" label="Debug" default="true"/>',
        '\t</category>',
        '\t<category label="Scrapers 1">'
    ]

    scrapers = sorted(relevant_scrapers(include_disabled=True), key=lambda x: x.name.lower())

    category_number = 2
    category_scraper_number = 0
    for scraper in scrapers:
        if category_scraper_number > 50:
            new_xml.append('\t</category>')
            new_xml.append('\t<category label="Scrapers %s">' % (category_number))
            category_number += 1
            category_scraper_number = 0
        new_xml.append('\t\t<setting label="%s" type="lsep"/>' % (scraper.name))
        scraper_xml = scraper.get_settings_xml()
        new_xml += ['\t\t' + line for line in scraper_xml]
        category_scraper_number += len(scraper_xml) + 1

    new_xml.append('\t</category>')
    new_xml.append('</settings>')

    try:
        with open(settings_location, 'r') as f:
            old_xml = f.read()
    except:
        old_xml = ''

    new_xml = '\n'.join(new_xml)


    if old_xml != new_xml:
        try:
            with open(settings_location, 'w') as f:
                f.write(new_xml)
        except:
            pass


#_update_settings_xml()
