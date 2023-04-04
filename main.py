# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-02-12 06:25:49
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-03 01:03:29
# FilePath: \Flow.Launcher.Plugin.ChromeBookmarks\main.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
import sys
import os
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
from WoxPluginBase_ChromeQuery import *

class BookmarksQuery(ChromeQuery):
    __actionKeyword__ = None

    def _getDatas_(self):
        return ChromeCache.getBookmarks()

    def _getResult_(self, regex:RegexList, data:Bookmark):
        BookmarksQuery.__actionKeyword__ = None
        if BookmarksQuery.__actionKeyword__ is None:
            with(
                open('./plugin.json','r') as pluginJson
            ):
                plugInID = json.load(pluginJson)['ID']
                BookmarksQuery.__actionKeyword__ = BookmarksQuery.GetActionKeyword(plugInID)

        item = f'{data.platform.name};{data.title};{data.path};{data.url}/'
        if not regex.match(item):
            return
        match data.type:
            case Bookmark.Type.url:
                return QueryResult(data.platform.name + ' ' + data.title, data.url, data.icon, self._datas_.index(data), self._openUrl_.__name__, True, data.url).toDict()
            case Bookmark.Type.folder:
                if data.url == regex.queryString:
                    # if right in the quering folder, not return it
                    return
                return QueryResult(data.platform.name + ' '  + data.title, data.url, data.icon, self._datas_.index(data), Launcher.GetAPI(Launcher.API.ChangeQuery), False, BookmarksQuery.__actionKeyword__ + ' ' + data.platform.name + ' '  + data.url, True).toDict()

    def _extraContextMenu_(self, data:Bookmark):
        return [self.getCopyDataResult('Directory', data.directory, ChromeData.FOLDER_ICON)]

if __name__ == '__main__':
    BookmarksQuery()