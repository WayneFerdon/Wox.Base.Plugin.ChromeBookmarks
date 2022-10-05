# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:08:29
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-05 17:58:10
# FilePath: \Wox.Plugin.ChromeBookmarks\ChromeCache.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
import json
import os
import sqlite3
import shutil
from enum import Enum

class Platform(Enum):
    Chrome = 0,
    Edge = 1

def GetInternalUrl(id: int):
    if id == 0 or id == 1:
        return 'chrome://bookmarks'
    return 'chrome://bookmarks/?id=' + str(id)

class ChromeData():
    class Type(Enum):
        url = 0, 
        folder = 1, 
    
    def __init__(self, title:str, url:str, type:Type=Type.url):
        self.title = title
        self.url = url
        self.type = type
        self.iconID = 0

class Bookmark(ChromeData):
    def __init__(self, title:str, url:str, path:str, id:int, directoryID:int, type:ChromeData.Type=ChromeData.Type.url):
        ChromeData.__init__(self, title,url,type)
        self.path = path
        self.id = id
        self.directory = GetInternalUrl(directoryID)

class History(ChromeData):
    def __init__(self, title:str, url:str, lastVisitTime:int, iconID:int):
        ChromeData.__init__(self, title, url)
        self.lastVisitTime = lastVisitTime

class Cache:
    def __init__(self, TargetPlatform):
        localAppData = os.environ['localAppData'.upper()]
        if(TargetPlatform == Platform.Chrome):
            self.__dataPath__ = localAppData + '/Google/Chrome/User Data/Default'
        elif(TargetPlatform == Platform.Edge):
            self.__dataPath__ = localAppData + '/Microsoft/Edge/User Data/Default'
        
        if(TargetPlatform == Platform.Chrome):
            self.PlatformIcon = './Images/chromeIcon.png'
        elif(TargetPlatform == Platform.Edge):
            self.PlatformIcon = './Images/edgeIcon.png'

        bitmapInfos, self.iconDict = self._iconInfo_()
        for iconID in bitmapInfos.keys():
            imageData = bitmapInfos[iconID]['imageData']
            try:
                with open('./Images/icon{}.png'.format(iconID), 'wb') as f:
                    f.write(imageData)
            except PermissionError:
                pass

    def _iconData_(self) -> str:
        favIcons = self.__dataPath__ + '/Favicons'
        iconData = self.__dataPath__ + '/FaviconsToRead'
        shutil.copyfile(favIcons, iconData)
        return iconData

    def _hisData_(self) -> str:
        history = self.__dataPath__ + '/History'
        hisData = self.__dataPath__ + '/HistoryToRead'
        shutil.copyfile(history, hisData)
        return hisData

    def _loadBookmarkData_(self) -> str:
        bookmark = self.__dataPath__ + '/Bookmarks'
        with open(bookmark, 'r', encoding='UTF-8') as f:
            bookmarkData = json.load(f)
        return bookmarkData

    def _loadIconData_(self) -> tuple[list, list]:
        cursor = sqlite3.connect(self._iconData_()).cursor()
        bitmapCursorResults = cursor.execute(
            'SELECT icon_id, image_data, width, height '
            'FROM favicon_bitmaps'
        ).fetchall()
        urlCursorResults = cursor.execute(
            'SELECT page_url, icon_id '
            'FROM icon_mapping'
        ).fetchall()
        cursor.close()
        return bitmapCursorResults, urlCursorResults

    def _loadHisData_(self) -> list:
        cursor = sqlite3.connect(self._hisData_()).cursor()
        hisInfoList = cursor.execute(
            'SELECT urls.url, urls.title, urls.last_visit_time '
            'FROM urls, visits '
            'WHERE urls.id = visits.url'
        ).fetchall()
        cursor.close()
        return hisInfoList

    def _iconInfo_(self) -> tuple[dict, dict]:
        bitmapList, urlList = self._loadIconData_()
        bitmapInfoList = dict()
        for iconID, imageData, width, height in bitmapList:
            if iconID in bitmapInfoList.keys():
                if (
                        width < bitmapInfoList[iconID]['width']
                        or height < bitmapInfoList[iconID]['height']
                ):
                    continue
            bitmapInfoList.update(
                {
                    iconID: {
                        'imageData': imageData, 
                        'width': width, 
                        'height': height
                    }
                }
            )
        iconList = dict()
        for url, iconID in urlList:
            if url not in iconList.keys():
                iconList.update(
                    {
                        url: iconID
                    }
                )
        return bitmapInfoList, iconList

    def getHistories(self) -> list[History]:
        historyInfos = self._loadHisData_()
        iconDict = self.iconDict
        histories = list[History]()
        items = list[str]()
        for url, title, lastVisitTime in historyInfos:
            item = url + title
            if item in items:
                itemIndex = items.index(item)
                if histories[itemIndex].lastVisitTime < lastVisitTime:
                    histories[itemIndex].lastVisitTime = lastVisitTime
            else:
                items.append(item)
                if url in iconDict.keys():
                    iconID = iconDict[url]
                else:
                    iconID = 0
                histories.append(History(title,url,lastVisitTime,iconID))
        histories.sort(key=lastVisitTime, reverse=True)
        return histories

    def getBookmarks(self) -> list[Bookmark]:
        bookmarks = list[Bookmark]()
        data = self._loadBookmarkData_()
        iconDict = self.iconDict
        for root in data['roots']:
            try:
                childItems = data['roots'][root]['children']
            except Exception:
                continue
            bookmarks.append(
                Bookmark(root, root, GetInternalUrl(0), data['roots'][root]['id'], 0, Bookmark.Type.folder)
            )
            bookmarks += self.getChildren(childItems, root, 0)

        for index in range(len(bookmarks)):
            url = bookmarks[index].url
            if url in iconDict.keys():
                bookmarks[index].iconID = iconDict[url]
            else:
                bookmarks[index].iconID = 0
        return bookmarks
    
    def getChildren(self, children:dict, ancestors:str, parentID:int) -> list[Bookmark]:
        items = list()
        for item in children:
            title, id = item['name'], item['id']
            type = Bookmark.Type[item['type']]
            if type == Bookmark.Type.url:
                url = item['url']
            else: # type == Bookmark.Type.folder
                url = ancestors + '/' + item['name']
                items += self.getChildren(item['children'], url, id)
            items.append(Bookmark(title, url, ancestors, id, parentID, type))
        return items
