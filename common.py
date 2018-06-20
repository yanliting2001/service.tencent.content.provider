#!/usr/bin/python
# -*- coding: utf-8 -*-

import xbmc
import xbmcaddon
import traceback
import urllib
import time

ADDON = xbmcaddon.Addon()
ADDON_NAME = ADDON.getAddonInfo('name')


def log(txt):
    message = '%s: %s' % (ADDON_NAME, txt.encode('ascii', 'ignore'))
    xbmc.log(msg=message, level=xbmc.LOGDEBUG)


def print_exc():
    traceback.print_exc()


def item_remap(detail, landscape, is_tvshow=False):
    tencent_id = detail['c_id']
    art_dict = {"fanart": detail['cover_pictures']['pic_1920x1080'],
                "landscape": landscape,
                "poster": detail['cover_pictures']['pic_770x1080']}
    casts = []
    str_id = "tvshowid" if is_tvshow else "movieid"
    for (count, k) in enumerate(detail['star_infos']):
        item = {"name": k['star_name'],
                "order": count,
                "role": "",
                "thumbnail": k['face_url']}
        casts.append(item)
    return {
        "art": art_dict,
        "cast": casts,
        "country": detail.get('area_name').split(','),
        "dateadded": detail.get('publish_date'),
        "director": detail.get('directors'),
        "file": "plugin://plugin.proxy.tencent.movies/play/tv/" + tencent_id if is_tvshow else "plugin://plugin.proxy.tencent.movies/play/" + tencent_id,
        "genre": [],
        "imdbnumber": "",
        "label": detail.get('title'),
        "lastplayed": "",
        str_id: tencent_id,
        "mpaa": "",
        "originaltitle": detail.get('title'),
        "playcount": 0,
        "plot": detail.get('c_description'),
        "plotoutline": detail.get('c_description'),
        "rating": '0.0' if not detail.get('score') else detail.get('score'),
        "resume": {"position": 0, "total": 0},
        "runtime": 0,
        "streamdetails": {},
        "studio": [],
        "tagline": detail.get('s_title'),
        "title": detail.get('title'),
        "trailer": "",
        "votes": "",
        "writer": [],
        "year": detail.get('year')
    }


def item_episode(data, tv_item):
    listitem = {}
    video_num = data['data']['video_num']
    episode = data['data']['videos'][0]
    vid = episode['v_id']
    listitem["art"] = {"season.poster": tv_item['art']['poster'],
                       "thumb": episode['v_ext_info']['pic_228x128'],
                       "tvshow.fanart": tv_item['art']['fanart'],
                       "tvshow.poster": tv_item['art']['poster']}
    listitem["cast"] = tv_item['cast']
    listitem["dateadded"] = episode['create_time']
    listitem["director"] = tv_item['director']
    listitem["episode"] = video_num
    listitem["episodeid"] = vid
    listitem["file"] = "plugin://plugin.proxy.tencent.movies/play/" + vid
    listitem["firstaired"] = tv_item['dateadded']
    listitem["label"] = episode['v_title']
    listitem["lastplayed"] = 0
    listitem["playcount"] = 0
    listitem["plot"] = tv_item['plot']
    listitem["rating"] = 0
    listitem["resume"] = tv_item['resume']
    listitem["runtime"] = episode['duration']
    listitem["season"] = 1
    listitem["showtitle"] = tv_item['tagline']
    listitem["streamdetails"] = tv_item['streamdetails']
    listitem["title"] = tv_item['label']
    listitem["tvshowid"] = tv_item['tvshowid']
    listitem["writer"] = tv_item['writer']
    return listitem


def create_json_rpc(listitems, channel):
    json_query = {}
    json_query['id'] = 1
    json_query['jsonrpc'] = 2.0
    if listitems:
        json_query['result'] = {}
        json_query['result'][channel] = listitems
    return json_query


def set_image_path(url):
    path = "image://"
    if url:
        path = path + urllib.quote_plus(url) + "/"
    return path


def get_datetime_str():
    return time.strftime("%Y-%m-%d") + " " + time.strftime("%H:%M:%S")
