# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-02-12 06:25:49
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-23 16:58:56
# FilePath: \FlowLauncher\Plugins\Wox.Base.Plugin.ChromeBookmarks\main.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
import sys
sys.path.append("../WoxBasePluginChromeQuery")
from ChromeQuery import *

class BookmarksQuery(ChromeQuery):
    def __getDatas__(self):
        return ChromeCache.getBookmarks()

    def __getResult__(self, regex:RegexList, data:Bookmark):
        item = f'{data.platform.name};{data.title};{data.path};{data.url}/'
        if not regex.match(item):
            return
        match data.type:
            case Bookmark.Type.url:
                return QueryResult(data.platform.name + data.title, data.url, data.icon, self.__datas__.index(data), self.openUrl.__name__, True, data.url).toDict()
            case Bookmark.Type.folder:
                if data.url == regex.queryString:
                    # if right in the quering folder, not return it
                    return
                return QueryResult(data.platform.name + data.title, data.url, data.icon, self.__datas__.index(data), LauncherAPI.ChangeQuery.name, False, Plugin.actionKeyword + ' ' + data.platform.name + ' '  + data.url, True).toDict()

    def __extraContextMenu__(self, data:Bookmark):
        return [self.getCopyDataResult('Directory', data.directory, ChromeData.FOLDER_ICON), self.getCopyDataResult('Directory', data.directory, ChromeData.FOLDER_ICON)]

if __name__ == '__main__':
    BookmarksQuery()