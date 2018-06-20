#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2012 Team-XBMC
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#    This script is based on service.skin.widgets
#    Thanks to the original authors

import xbmc
import xbmcgui
import xbmcaddon
import json
from time import gmtime, strftime
from tencent import TencentClass
from common import *
from cache import CacheFunc


PLOT_ENABLE = True


class LibraryFunctions():

    def __init__(self):
        self.WINDOW = xbmcgui.Window(10000)
        self.LIMIT = int(xbmcaddon.Addon().getSetting("limit"))
        self.RECENTITEMS_UNPLAYED = xbmcaddon.Addon().getSetting("recentitems_unplayed") == 'true'
        self.RANDOMITEMS_UNPLAYED = xbmcaddon.Addon().getSetting("randomitems_unplayed") == 'true'
        self.INCLUDE_SPECIALS = xbmcaddon.Addon().getSetting("include_specials") == 'true'
        self.TENCENT = TencentClass()
        self.CACHE = CacheFunc()

    def _get_data(self, query_type, useCache):
        # Check if data is being refreshed elsewhere
        if self.WINDOW.getProperty(query_type + "-data") == "LOADING":
            for count in range(30):
                xbmc.sleep(100)
                data = self.WINDOW.getProperty(query_type + "-data")
                if data != "LOADING":
                    return data

        if useCache:
            # Check whether there is saved data
            if self.WINDOW.getProperty(query_type + "-data") is not "":
                return self.WINDOW.getProperty(query_type + "-data")

        # We haven't got any data, so don't send back anything
        return None

    # Common infrastructure for all queries: Use the cache if specified,
    # set the property to "LOADING" while the query runs,
    # set the timestamp and property correctly
    def _fetch_items(self, useCache=False, prefix=None, queryFunc=None):
        data = self._get_data(prefix, useCache)
        if data is not None:
            return data
        self.WINDOW.setProperty(prefix + "-data", "LOADING")

        rv = queryFunc()  # Must return a unicode string (json-encoded data)

        self.WINDOW.setProperty(prefix + "-data", rv)
        self.WINDOW.setProperty(prefix, strftime("%Y%m%d%H%M%S", gmtime()))
        return rv

    # Common properties used by various types of queries
    movie_properties = [
                            "title",
                            "originaltitle",
                            "votes",
                            "playcount",
                            "year",
                            "genre",
                            "studio",
                            "country",
                            "tagline",
                            "plot",
                            "runtime",
                            "file",
                            "plotoutline",
                            "lastplayed",
                            "trailer",
                            "rating",
                            "resume",
                            "art",
                            "streamdetails",
                            "mpaa",
                            "director",
                            "writer",
                            "cast",
                            "dateadded",
                            "imdbnumber"]
    tvepisode_properties = [
                            "title",
                            "playcount",
                            "season",
                            "episode",
                            "showtitle",
                            "plot",
                            "file",
                            "rating",
                            "resume",
                            "tvshowid",
                            "art",
                            "streamdetails",
                            "firstaired",
                            "runtime",
                            "director",
                            "writer",
                            "cast",
                            "dateadded",
                            "lastplayed"]
    tvshow_properties = [
                            "title",
                            "studio",
                            "mpaa",
                            "file",
                            "art"]
    music_properties = [
                            "title",
                            "playcount",
                            "genre",
                            "artist",
                            "album",
                            "year",
                            "file",
                            "thumbnail",
                            "fanart",
                            "rating",
                            "lastplayed"]
    album_properties = [
                            "title",
                            "description",
                            "albumlabel",
                            "theme",
                            "mood",
                            "style",
                            "type",
                            "artist",
                            "genre",
                            "year",
                            "thumbnail",
                            "fanart",
                            "rating",
                            "playcount"]
    musicvideo_properties = [
                            "title",
                            "artist",
                            "playcount",
                            "studio",
                            "director",
                            "year",
                            "plot",
                            "genre",
                            "runtime",
                            "art",
                            "file",
                            "streamdetails",
                            "resume"]

    # Common sort/filter arguments shared by multiple queries
    recent_sort = {"order": "descending", "method": "dateadded"}
    unplayed_filter = {"field": "playcount", "operator": "lessthan", "value": "1"}
    specials_filter = {"field": "season", "operator": "greaterthan", "value": "0"}
    inprogress_filter = {"field": "inprogress", "operator": "true", "value": ""}

    # Construct a JSON query string from the arguments, execute it, return UTF8
    def json_query(self, method, unplayed=False, include_specials=True, properties=None, sort=False,
                   query_filter=False, limit=False, params=False):
        # Set defaults if not all arguments are passed in
        if sort is False:
            sort = {"method": "random"}
        if properties is None:
            properties = self.movie_properties
        if unplayed:
            query_filter = self.unplayed_filter if not query_filter else {"and": [self.unplayed_filter, query_filter]}
        if not include_specials:
            query_filter = self.specials_filter if not query_filter else {"and": [self.specials_filter, query_filter]}

        json_query = {"jsonrpc": "2.0", "id": 1, "method": method, "params": {}}

        # As noted in the docstring, False = use a default, None=omit entirely
        if properties is not None:
            json_query["params"]["properties"] = properties
        if limit is not None:
            json_query["params"]["limits"] = {"end": limit if limit else self.LIMIT}
        if sort is not None:
            json_query["params"]["sort"] = sort
        if query_filter:
            json_query["params"]["filter"] = query_filter
        if params:
            json_query["params"].update(params)

        json_string = json.dumps(json_query)
        rv = xbmc.executeJSONRPC(json_string)

        return unicode(rv, 'utf-8', errors='ignore')

    def json_query_recommended(self, channel, limit=20):
        result = self._fetch_channel_recommended(channel)
        is_tvshow = False if channel not in ["tv", "children", "cartoon"] else True
        channel_str = "movies" if channel not in ["tv", "children", "cartoon"] else "tvshows"
        listitems = []
        count = 0
        for module in result:
            for item in module['items']:
                comm_data = item['comm_item']
                if not comm_data['item_type'] in ["album", "topic"]:
                    continue
                detail_data = self._fetch_video_detail(comm_data['item_id'])
                if not detail_data:
                    continue
                listitem = item_remap(detail_data['data'], comm_data['pic_722x354'], is_tvshow)
                listitems.append(listitem)
            count += 1
            if count == limit - 1:
                break
        json_query = create_json_rpc(listitems, channel_str)
        rv = json.dumps(json_query)

        return unicode(rv, 'utf-8', errors='ignore')

    def json_query_episode(self, item):
        cid = item['tvshowid']
        result = self._fetch_video_episodelist(cid, 0)
        listitems = []
        if result:
            listitem = item_episode(result, item)
            listitems.append(listitem)
        json_query = create_json_rpc(listitems, "episodes")
        rv = json.dumps(json_query)

        return unicode(rv, 'utf-8', errors='ignore')

    # These functions default to random items.
    # By sorting differently they'll also be used for recent items.
    def _fetch_random_movies(self, useCache=False, sort=False, prefix="randommovies"):
        unplayed_flag = self.RANDOMITEMS_UNPLAYED if prefix == "randommovies" else self.RECENTITEMS_UNPLAYED

        def query_random_movies():
            return self.json_query("VideoLibrary.GetMovies", unplayed=unplayed_flag, sort=sort)
        return self._fetch_items(useCache, prefix, query_random_movies)

    def _fetch_random_episodes(self, useCache=False, sort=False, prefix="randomepisodes"):
        unplayed_flag = self.RANDOMITEMS_UNPLAYED if prefix == "randommovies" else self.RECENTITEMS_UNPLAYED

        def query_randomepisodes():
            return self.json_query("VideoLibrary.GetEpisodes", unplayed=unplayed_flag,
                                   include_specials=self.INCLUDE_SPECIALS,
                                   properties=self.tvepisode_properties, sort=sort)
        return self._fetch_items(useCache, prefix, query_randomepisodes)

    def _fetch_random_songs(self, useCache=False, sort=False):
        def query_randomsongs():
            return self.json_query("AudioLibrary.GetSongs", unplayed=self.RANDOMITEMS_UNPLAYED,
                                   properties=self.music_properties, sort=sort)
        return self._fetch_items(useCache, "randomsongs", query_randomsongs)

    def _fetch_random_albums(self, useCache=False, sort=False, prefix="randomalbums"):
        def query_randomalbums():
            return self.json_query("AudioLibrary.GetAlbums", properties=self.album_properties, sort=sort)
        return self._fetch_items(useCache, prefix, query_randomalbums)

    def _fetch_random_musicvideos(self, useCache=False, sort=False, prefix="randommusicvideos"):
        unplayed_flag = self.RANDOMITEMS_UNPLAYED if prefix == "randommusicvideos" else self.RECENTITEMS_UNPLAYED

        def query_musicvideos():
            return self.json_query("VideoLibrary.GetMusicVideos", unplayed=unplayed_flag,
                                   properties=self.musicvideo_properties, sort=sort)
        return self._fetch_items(useCache, prefix, query_musicvideos)

    # _fetch_recent_* is the same as the random ones except for sorting
    def _fetch_recent_movies(self, useCache=False):
        return self._fetch_random_movies(useCache, sort=self.recent_sort, prefix="recentmovies")

    def _fetch_recent_episodes(self, useCache=False):
        return self._fetch_random_episodes(useCache, sort=self.recent_sort, prefix="recentepisodes")

    def _fetch_recent_albums(self, useCache=False):
        return self._fetch_random_albums(useCache, sort=self.recent_sort, prefix="recentalbums")

    def _fetch_recent_musicvideos(self, useCache=False):
        return self._fetch_random_musicvideos(useCache, sort=self.recent_sort, prefix="recentmusicvideos")

    # Recommended movies: movies that are in progress
    def _fetch_recommended_movies(self, useCache=False):
        def query_recommended_movies():
            return self.json_query_recommended("movie")
        return self._fetch_items(useCache, "recommendedmovies", query_recommended_movies)

    # Recommended varieties
    def _fetch_recommended_varieties(self, useCache=False):
        def query_recommended_varieties():
            return self.json_query_recommended("variety")
        return self._fetch_items(useCache, "recommendedvarieties", query_recommended_varieties)

    # Recommended nba
    def _fetch_recommended_nba(self, useCache=False):
        def query_recommended_nba():
            return self.json_query_recommended("nba")
        return self._fetch_items(useCache, "recommendednba", query_recommended_nba)

    # Recommended physical
    def _fetch_recommended_physical(self, useCache=False):
        def query_recommended_physical():
            return self.json_query_recommended("physical_pay")
        return self._fetch_items(useCache, "recommendedphysical", query_recommended_physical)

    # Recommended episodes: Earliest unwatched episode from in-progress shows
    def _fetch_recommended_episodes(self, useCache=False):
        def query_recommended_episodes():
            # First we get a list of all the in-progress TV shows.
            json_query_string = self.json_query_recommended("tv")
            json_query = json.loads(json_query_string)

            # If we found any, find the oldest unwatched show for each one.
            if "result" in json_query and 'tvshows' in json_query['result']:
                for item in json_query['result']['tvshows']:
                    if xbmc.abortRequested:
                        break
                    json_query2 = self.json_query_episode(item)
                    self.WINDOW.setProperty("recommended-episodes-data-%s"
                                            % item['tvshowid'], json_query2)
            return json_query_string
        return self._fetch_items(useCache, "recommendedepisodes", query_recommended_episodes)

    def _fetch_recommended_children(self, useCache):
        def query_recommended_children():
            json_query_string = self.json_query_recommended("children")
            json_query = json.loads(json_query_string)

            if "result" in json_query and 'tvshows' in json_query['result']:
                for item in json_query['result']['tvshows']:
                    if xbmc.abortRequested:
                        break
                    json_query2 = self.json_query_episode(item)
                    self.WINDOW.setProperty("recommended-children-data-%s"
                                            % item['tvshowid'], json_query2)
            return json_query_string
        return self._fetch_items(useCache, "recommendedchildren", query_recommended_children)

    def _fetch_recommended_cartoon(self, useCache):
        def query_recommended_cartoon():
            json_query_string = self.json_query_recommended("cartoon")
            json_query = json.loads(json_query_string)

            if "result" in json_query and 'tvshows' in json_query['result']:
                for item in json_query['result']['tvshows']:
                    if xbmc.abortRequested:
                        break
                    json_query2 = self.json_query_episode(item)
                    self.WINDOW.setProperty("recommended-cartoon-data-%s"
                                            % item['tvshowid'], json_query2)
            return json_query_string
        return self._fetch_items(useCache, "recommendedcartoon", query_recommended_cartoon)

    # Recommended albums are just the most-played ones
    def _fetch_recommended_albums(self, useCache=False):
        def query_recommended():
            return self.json_query("AudioLibrary.GetAlbums", properties=self.album_properties,
                                   sort={"order": "descending", "method": "playcount"})
        return self._fetch_items(useCache, "recommendedalbums", query_recommended)

    # Favourite episodes are the oldest unwatched episodes
    # from shows that are in your favourites list
    def _fetch_favourite_episodes(self, useCache=False):
        def query_favourite():
            # Get all favourites and all unwatched shows
            # store their intersection in fav_unwatched
            favs = json.loads(self.json_query("Favourites.GetFavourites", unplayed=False,
                                              properties=[], sort=None, query_filter=None, limit=None))
            if favs['result']['favourites'] is None:
                return None
            shows = json.loads(self.json_query("VideoLibrary.GetTVShows", unplayed=True,
                                               properties=self.tvshow_properties, limit=None))
            if "result" not in shows or 'tvshows' not in shows['result']:
                return None
            fav_unwatched = [show for show in shows['result']['tvshows']
                             if show['title'] in set([fav['title']
                                                     for fav in favs['result']['favourites']
                                                     if fav['type'] == 'window'])]

            # Skeleton return data, to be built out below...
            rv = {u'jsonrpc': u'2.0', u'id': 1, u'result': {u'tvshows': [],
                  u'limits': {u'start': 0, u'total': 0, u'end': 0}}}
            # Find the oldest unwatched episode for each fav_unwatched
            # Add it to the rv; store data in a per-show property
            for fav in fav_unwatched:
                show_info_string = self.json_query("VideoLibrary.GetEpisodes", unplayed=True,
                                                   include_specials=self.INCLUDE_SPECIALS,
                                                   properties=self.tvepisode_properties,
                                                   params={"tvshowid": fav['tvshowid']},
                                                   sort={"method": "episode"}, limit=1,
                                                   query_filter=self.unplayed_filter)
                show_info = json.loads(show_info_string)
                if show_info['result']['limits']['total'] > 0:
                    rv['result']['tvshows'].append(fav)
                    rv['result']['limits']['total'] += 1
                    rv['result']['limits']['end'] += 1
                    self.WINDOW.setProperty("favouriteepisodes-data-%d"
                                            % fav['tvshowid'], show_info_string)

            return unicode(json.dumps(rv), 'utf-8', errors='ignore')
        return self._fetch_items(useCache, prefix="favouriteepisodes", queryFunc=query_favourite)

    def _fetch_channel_recommended(self, channel, useCache=True):
        if useCache:
            data = self.CACHE.get_cache_data("tencent_channelrecommended", channel)
            try:
                if data is not None and len(data) > 0:
                    return data
            except Exception:
                    log("old format cache")
        data = self.TENCENT.get_channel_recommended(channel)
        data = json.loads(data)
        result = None
        if "result" in data and data['result']['ret'] == 0 and len(data['data']['channel_contents']) > 0:
            self.CACHE.set_cache_data("tencent_channelrecommended", data['data']['channel_contents'][0]['modules'], channel, 0)
            result = data['data']['channel_contents'][0]['modules']
        return result

    def _fetch_video_detail(self, cid, useCache=True):
        if useCache:
            data = self.CACHE.get_cache_data("tencent_videodetail", cid)
            if data and data['data'].get('c_id'):
                return data
        data = self.TENCENT.get_video_detail(cid)
        data = json.loads(data)
        if data and data['result']['ret'] == 0:
            self.CACHE.set_cache_data("tencent_videodetail", data, cid)
            return data
        return None

    def _fetch_video_episodelist(self, cid, index, useCache=True):
        if useCache:
            data = self.CACHE.get_cache_data("tencent_tvshowepisodelist", cid + str(index))
            if data and data['data'].get('videos'):
                return data
        data = self.TENCENT.get_episodelist(cid, index)
        data = json.loads(data)
        if data and "result" in data and data['result']['ret'] == 0:
            self.CACHE.set_cache_data("tencent_tvshowepisodelist", data, cid + str(index))
            return data
        return None
