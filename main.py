# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-02-12 06:25:49
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-05 18:14:02
# FilePath: \Wox.Plugin.ChromeBookmarks\main.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
from ChromeWox import *

FOLDER_ICON = './Images/folderIcon.png'

class GetBookmarks(ChromeWox):
    def getDatas(self):
        return self.cache.getBookmarks

    def getResult(self, regex, data:Bookmark):
        item = data.title + data.url + data.path + '/'
        if not regex.match(item):
            return
        if data.type == Bookmark.Type.url:
            if data.iconID != 0:
                iconPath = './Images/icon{}.png'.format(data.iconID)
            else:
                iconPath = self.PlatformIcon
            return WoxResult(data.title, data.url, iconPath, self.datas.index(data), self.openUrl.__name__, True, data.url).toDict()
        else: # bookmark.type == Bookmark.Type.folder
            if data.url + '/' in regex.queryString:
                # if already in target folder
                return
            return WoxResult(data.title, data.url, FOLDER_ICON, self.datas.index(data), 'Wox.ChangeQuery', False, 'bm ' + data.url + '/', True).toDict()

    def extraContextMenu(self, data:Bookmark, iconPath):
        return [self.getCopyDataResult('Directory', data.directory, iconPath)]

if __name__ == '__main__':
    GetBookmarks()
    # GetBookmarks().query('')