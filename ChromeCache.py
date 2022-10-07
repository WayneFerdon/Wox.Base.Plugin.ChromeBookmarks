# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:08:29
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-07 20:21:13
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

@staticmethod
def getInternalUrl(id: int):
    if id == 0 or id == 1:
        return 'chrome://bookmarks/'
    return 'chrome://bookmarks/?id=' + str(id) + '/'

class ChromeData():
    class Type(Enum):
        url = 0, 
        folder = 1, 

    def __init__(self, title:str, url:str, type:Type=Type.url):
        self.title = title
        self.url = url
        self.type = type
        match type:
            case ChromeData.Type.folder:
                self.icon = ChromeData.FOLDER_ICON
            case ChromeData.Type.url:
                iconID = Cache.getIconID(self.url)
                if iconID != 0:
                    iconPath = ChromeData.__getIconPath__(iconID)
                else:
                    iconPath = Cache.PLATFORM_ICON
                self.icon = ChromeData.__getAbsPath__(iconPath)

    @staticmethod
    def __getAbsPath__(iconPath):
        return os.path.join(os.path.abspath('./'), iconPath)

    FOLDER_ICON = __getAbsPath__('./Images/folderIcon.png')

    @staticmethod
    def __getIconPath__(iconID):
        return './Images/Temp/icon{}.png'.format(iconID)

class Bookmark(ChromeData):
    def __init__(self, title:str, url:str, path:str, id:int, directoryID:int, type:ChromeData.Type):
        ChromeData.__init__(self, title, url, type)
        self.path = path
        self.id = id
        self.directory = getInternalUrl(directoryID)

class History(ChromeData):
    def __init__(self, title:str, url:str, lastVisitTime:int):
        ChromeData.__init__(self, title, url)
        self.lastVisitTime = lastVisitTime

class BitMap():
    def __init__(self, image, width, height) -> None:
        self.image = image
        self.width = width
        self.height = height

class Cache:
    @staticmethod
    def getIconID(url):
        for keyURL in Cache.__ICON_DICT__.keys():
            if url in keyURL:
                return Cache.__ICON_DICT__[keyURL]
        return 0

    @staticmethod
    def getHistories() -> list[History]:
        historyInfos = Cache.__loadHistories__()
        histories = dict[str, History]()
        for url, title, lastVisitTime in historyInfos:
            key = url + title
            if key not in histories.keys():
                histories[key] = History(title, url, lastVisitTime)
                continue
            if histories[key].lastVisitTime >= lastVisitTime:
                continue
            histories[key].lastVisitTime = lastVisitTime
        histories = list(histories.values())
        histories.sort(key=lambda history:history.lastVisitTime, reverse=True)
        return histories

    @staticmethod
    def getBookmarks() -> list[Bookmark]:
        def getChildren(children:dict, ancestors:str, parentID:int) -> list[Bookmark]:
            bookmarks = list()
            for item in children:
                title, id = item['name'], item['id']
                type = Bookmark.Type[item['type']]
                match type:
                    case Bookmark.Type.url:
                        url = item['url']
                    case Bookmark.Type.folder:
                        url = ancestors + item['name'] + '/'
                        bookmarks += getChildren(item['children'], url, id)
                bookmarks.append(Bookmark(title, url, ancestors, id, parentID, type))
            return bookmarks
        
        data = Cache.__loadBookmarks__()
        bookmarks = list[Bookmark]()
        for root in data['roots']:
            try:
                childItems = data['roots'][root]['children']
            except Exception:
                continue

            bookmarks.append(Bookmark(root, root+ '/', getInternalUrl(0), data['roots'][root]['id'], 0, Bookmark.Type.folder))
            bookmarks += getChildren(childItems, root + '/', 0)
        return bookmarks

    @staticmethod
    def __init__(TargetPlatform):
        Cache.__setPlatform__(TargetPlatform)
        Cache.__loadcons__()
    
    @staticmethod
    def __setPlatform__(TargetPlatform):
        localAppData = os.environ['localAppData'.upper()]
        match TargetPlatform:
            case Platform.Chrome:
                Cache.PLATFORM_ICON = './Images/chromeIcon.png'
                Cache.__DATA_PATH__ = '/Google/Chrome/'
            case Platform.Edge:
                Cache.PLATFORM_ICON = './Images/edgeIcon.png'
                Cache.__DATA_PATH__ = '/Microsoft/Edge/'
        Cache.__DATA_PATH__ = localAppData + Cache.__DATA_PATH__ + 'User Data/Default/'

    @staticmethod
    def __loadcons__():
        cursor = sqlite3.connect(Cache.__getReadOnlyData__('Favicons')).cursor()
        bitmapCursorResults = cursor.execute(
            'SELECT icon_id, image_data, width, height '
            'FROM favicon_bitmaps'
        ).fetchall()
        urlCursorResults = cursor.execute(
            'SELECT page_url, icon_id '
            'FROM icon_mapping'
        ).fetchall()
        cursor.close()
        bitmaps, urls = bitmapCursorResults, urlCursorResults
        bitmapInfos = dict[int, BitMap]()

        for iconID, image, width, height in bitmaps:
            if iconID in bitmapInfos.keys() \
            and (width < bitmapInfos[iconID].width
            or height < bitmapInfos[iconID].height):
                continue
            bitmapInfos[iconID] = BitMap(image,width,height)
    
        Cache.__ICON_DICT__ = dict[str, int]()
        for url, iconID in urls:
            Cache.__ICON_DICT__[url] = iconID

        for iconID in bitmapInfos.keys():
            imageData = bitmapInfos[iconID].image
            try:
                with open(ChromeData.__getIconPath__(iconID), 'wb') as f:
                    f.write(imageData)
            except PermissionError:
                pass

    @staticmethod
    def __getReadOnlyData__(dataName):
        sourceData = Cache.__DATA_PATH__ + dataName
        readOnlyData = Cache.__DATA_PATH__ + dataName + 'ToRead'
        shutil.copyfile(sourceData, readOnlyData)
        return readOnlyData

    @staticmethod
    def __loadBookmarks__() -> str:
        with open(Cache.__DATA_PATH__ + 'Bookmarks', 'r', encoding='UTF-8') as f:
            bookmarkData = json.load(f)
        return bookmarkData

    @staticmethod
    def __loadHistories__() -> list:
        cursor = sqlite3.connect(Cache.__getReadOnlyData__('History')).cursor()
        histories = cursor.execute(
            'SELECT urls.url, urls.title, urls.last_visit_time '
            'FROM urls, visits '
            'WHERE urls.id = visits.url'
        ).fetchall()
        cursor.close()
        return histories
