#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#     Copyright (C) 2015 PivosGroup
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


import util
import os
from common import *


class TencentClass():
    HOST = 'tv.t002.ottcn.com'

    API = 'http://' + HOST + '/i-tvbin/qtv_video/'

    def get_channel_index(self):  # 频道索引
        return util.GetHttpData(self.API + 'channel_list/get_channel_list?tv_cgi_ver=1.0&format=json&req_from=PVS_APK&channel_types=all')

    def get_channel_recommended(self, channel):
        return util.GetHttpData(self.API + 'home_page/get_home_page?tv_cgi_ver=1.0&format=json&req_from=TCL_WX&req_type=get&channel_selector=specify&channel_ids={channel}&content_selector=all'.format(channel=channel))

    def get_special_recommended(self, channel):
        return util.GetHttpData(self.API + 'special_channel/get_special_channel?tv_cgi_ver=1.0&format=json&req_from=PVS_APK&req_type=get&channel_selector={channel}&content_selector=all'.format(channel=channel))

    def get_finance_combol(self): # 精选推荐
        return util.GetHttpData('http://aniuapi.dzcj.tv:8083/aniuapi/ottapi/v1/1905/videolist?productid={productid}&devid={devid}'.format(productid="10001", devid="200004"), use_qua=False)

    def get_channel_filter(self, channel):  # 频道筛选列表
        return util.GetHttpData(self.API + 'channel_filter/get_filter?tv_cgi_ver=1.0&format=json&req_from=PVS_APK&channel_selector={0}&filter_selector=single'.format(channel))

    def get_channel_list(self, channel, route, sort, filter_name, settype, page, pagenum):  # 频道列表
        url = self.API + 'video_list/get_video_list?platform=8&site={site}&filter={filter}&list_route_type={route}&sortby={sort}&fieldset={settype}&page={page}&pagesize={pagenum}&otype=json'
        url = url.format(
            site=channel,
            filter=filter_name,
            route=route,
            settype=settype,
            sort=sort,
            page=page,
            pagenum=pagenum
        )
        return util.GetHttpData(url)

    def get_like_recommend(self, cid):  # 猜你喜欢
        return util.GetHttpData(self.API + 'recommend/get_recommend_j?tv_cgi_ver=1.0&format=json&req_from=PVS_APK&cover_id={0}&req_num=10&pay_filter=0'.format(cid))

    def get_search(self, keyword, page=0, url=[], page_size=25):  # 搜索
        if page == 0:
            return util.GetHttpData(self.API + 'search/get_search_video?key={0}&page_size={1}&page_num=0&tabid=0&format=json&search_type=1&pay_filter=0&version=0'.format(keyword, page_size))
        else:
            return util.GetHttpData('http://' + self.HOST + url[page - 1], use_qua=False)

    def get_search_rank(self):
        return util.GetHttpData(self.API + 'search/get_search_rank?format=json')

    def get_video_detail(self, cid):  # 专辑详情
        return util.GetHttpData(self.API + 'cover_details/get_cover_basic?tv_cgi_ver=1.0&format=json&req_from=TCL_WX&start_type=head&video_num=0&video_filter=all&cid=' + cid)

    def get_finance_detail(self, prgid):  # 精选详情
        return util.GetHttpData('http://aniuapi.dzcj.tv:8083/aniuapi/ottapi/v1/1905/morevideo?productid={productid}&prgid={prgid}&devid={devid}'.format(productid="10001", prgid=prgid, devid="200004"))

    def get_finance_playinfo(self, contentid):
        return util.GetHttpData('http://aniuapi.dzcj.tv:8083/aniuapi/api/v1/tv/ottplayinfo?contentid={contentid}&devid={devid}'.format(contentid=contentid, devid="200004"))

    def get_variety_review(self, cid, pagesize=10, pagenum=0):  # 综艺往期
        return util.GetHttpData(self.API + 'column_info/get_column_info?column_id={0}&page_size={1}&page_num={2}&format=json&type=10'.format(cid, pagesize, pagenum))

    def get_still(self, cid):  # 剧照
        if self.LOCAL_DEBUG:
            json_query = open(os.path.join(ADDON_PATH, 'get_video_detail.txt')).read()
        else:
            json_query = util.GetHttpData('http://live.play.t002.ottcn.com/json/qzmovie/still/{0}/{1}.json'.format(cid[0], cid), None, None, False)
        return json_query[26:-2]

    def get_trailer(self, cid):  # 预告片
        return util.GetHttpData(self.API + 'get_trailer?version=1.0&format=json&platform=8&subplatform=41&cid=' + cid)

    def get_episodelist(self, cid, index):  # 剧集列表
        return util.GetHttpData(self.API + 'cover_details/get_cover_videos?tv_cgi_ver=1.0&format=json&req_from=TCL_WX&page_type=forward&page_start={0}&page_size=128&video_filter=all&cid={1}'.format(index, cid))

    def get_topic_detail(self, tid):  # 专题详情
        return util.GetHttpData(self.API + 'topic_detail/qtv_get_topic_detail?tid={0}&format=json&licence=icntv'.format(tid))

    def get_play_info(self, cid):
        url = self.API + 'get_play_info?format=json&cid={0}'.format(cid)
        return util.GetHttpData(url)


if __name__ == "__main__":
    a = TencentClass()
    # print a.get_channel_index()
    # print a.get_home_combol()
    # print a.get_channel_filter()
    # print a.get_search('天下')
    # print a.get_channel_recommend('movie+tv')
    # print a.get_channel_list('variety', filter='itype=1',sort=2,settype='media_cover',offset=0,pagenum=32)
    # print a.get_still('rhih15hy3olshm6')
    # print a.get_trailer('2i8x7hgirc27kgh')
    # print a.get_episodelist('9c50ost5k6vlehq')
    # print a.get_topic_detail(123)

    # print a.get_like_recommend('acegbmbuy0mjvx9')
    # print a.get_video_detail('9c50ost5k6vlehq')
