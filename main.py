# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from wox import Wox, WoxAPI
import re
import webbrowser
import json
import os
import win32con
import win32clipboard
import sqlite3
import shutil
from urllib.parse import urlparse

TargetPlatform = "Chrome" # Chrome, Edge

class regexList:
    def __init__(self, queryString):
        queryStringLower = queryString.lower()
        queryList = queryStringLower.split()
        self.regexList = list()
        for query in queryList:
            # pattern = '.*?'.join(query)
            # regexList.append(re.compile(pattern))
            self.regexList.append(re.compile(query))

    def match(self, item):
        match = True
        for regex in self.regexList:
            match = regex.search(item) and match
        return match


def createIcon(bitmapInfoList):
    for iconId in bitmapInfoList.keys():
        imageData = bitmapInfoList[iconId]['imageData']
        with open('./Images/iconId{}.png'.format(iconId), 'wb') as f:
            f.write(imageData)


def makeList(itemsList, childItems, pathFolder):
    for item in childItems:
        if item['type'] == 'folder':
            folderName = item['name']
            childPathFolder = pathFolder + '/' + folderName
            itemsList.append(
                {
                    'title': folderName,
                    'url': childPathFolder,
                    'path': pathFolder,
                    'type': 'folder'
                }
            )
            itemsList = makeList(itemsList, item['children'], childPathFolder)
        elif item['type'] == 'url':
            itemsList.append(
                {
                    'title': item['name'],
                    'url': item['url'],
                    'path': pathFolder,
                    'type': 'bookmark'
                }
            )
    return itemsList


class chromeCache:
    def __init__(self):
        localAppData = os.environ['localAppData'.upper()]
        if(TargetPlatform == "Chrome"):
            self.__dataPath__ = localAppData + '/Google/Chrome/User Data/Default'
        elif(TargetPlatform == "Edge"):
            self.__dataPath__ = localAppData + '/Microsoft/Edge/User Data/Default'
        self.bitmapInfoList, self.iconList = self._iconInfo_()

    def _iconData_(self):
        favIcons = self.__dataPath__ + '/Favicons'
        iconData = self.__dataPath__ + '/FaviconsToRead'
        shutil.copyfile(favIcons, iconData)
        return iconData

    def _hisData_(self):
        history = self.__dataPath__ + '/History'
        hisData = self.__dataPath__ + '/HistoryToRead'
        shutil.copyfile(history, hisData)
        return hisData

    def _loadBookmarkData_(self):
        bookmark = self.__dataPath__ + '/Bookmarks'
        with open(bookmark, 'r', encoding='UTF-8') as f:
            bookmarkData = json.load(f)
        return bookmarkData

    def _loadIconData_(self):
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

    def _loadHisData_(self):
        cursor = sqlite3.connect(self._hisData_()).cursor()
        hisInfoList = cursor.execute(
            'SELECT urls.url, urls.title, urls.last_visit_time '
            'FROM urls, visits '
            'WHERE urls.id = visits.url'
        ).fetchall()
        cursor.close()
        return hisInfoList

    def _iconInfo_(self):
        bitmapList, urlList = self._loadIconData_()
        bitmapInfoList = dict()
        for iconId, imageData, width, height in bitmapList:
            if iconId in bitmapInfoList.keys():
                if (
                        width < bitmapInfoList[iconId]['width']
                        or height < bitmapInfoList[iconId]['height']
                ):
                    continue
            bitmapInfoList.update(
                {
                    iconId: {
                        'imageData': imageData,
                        'width': width,
                        'height': height
                    }
                }
            )
        iconList = dict()
        for url, iconId in urlList:
            # netLocation = urlparse(url).netloc
            if url not in iconList.keys():
                iconList.update(
                    {
                        url: iconId
                    }
                )
        return bitmapInfoList, iconList

    def hisList(self):
        hisInfoList = self._loadHisData_()
        iconList = self.iconList
        hisList = list()
        items = list()
        for url, title, lastVisitTime in hisInfoList:
            item = url + title
            if item in items:
                itemIndex = items.index(item)
                if hisList[itemIndex]['lastVisitTime'] < lastVisitTime:
                    hisList[itemIndex]['lastVisitTime'] = lastVisitTime
            else:
                items.append(item)
                # netLocation = urlparse(url).netloc
                if url in iconList.keys():
                    iconId = iconList[url]
                else:
                    iconId = 0
                hisList.append(
                    {
                        'url': url,
                        'title': title,
                        'item': item,
                        'lastVisitTime': lastVisitTime,
                        'iconId': iconId
                    }
                )
        hisList.sort(key=timeFromHisList, reverse=True)
        return hisList

    def bookmarkList(self):
        bookmarkList = list()
        data = self._loadBookmarkData_()
        iconList = self.iconList
        for root in data['roots']:
            try:
                childItems = data['roots'][root]['children']
            except Exception:
                continue
            bookmarkList = makeList(bookmarkList, childItems, root)

        for index in range(len(bookmarkList)):
            url = bookmarkList[index]['url']
            # netLocation = urlparse(url).netloc
            if url in iconList.keys():
                bookmarkList[index]['iconId'] = iconList[url]
            else:
                bookmarkList[index]['iconId'] = 0
        return bookmarkList


# class getBookmarks:
class getBookmarks(Wox):
    cache = chromeCache()
    createIcon(cache.bitmapInfoList)
    bookmarkList = cache.bookmarkList()

    def query(self, queryString):
        folderIcon = './Images/folderIcon.png'
        result = list()
        bookmarkList = self.bookmarkList

        regex = regexList(queryString)

        for bookmark in bookmarkList:
            title = bookmark['title']
            url = bookmark['url']
            path = bookmark['path']
            item = title + url + path
            if regex.match(item.lower()):
                bookmarkIndex = bookmarkList.index(bookmark)
                type = bookmark['type']
                if type == 'folder':
                    if url in queryString:  # if already in target folder
                        result.insert(
                            0,
                            {
                                'Title': 'Parent: ' + path,
                                'SubTitle': 'Press Enter to Return to Parent Folder',
                                'IcoPath': folderIcon,
                                'ContextData': bookmarkIndex,
                                'JsonRPCAction': {
                                    'method': 'Wox.ChangeQuery',
                                    'parameters': ['bm ' + path, True],
                                    "doNotHideAfterAction".replace('oNo', 'on'): True
                                }
                            }
                        )
                    else:
                        result.append(
                            {
                                'Title': title,
                                'SubTitle': url,
                                'IcoPath': folderIcon,
                                'ContextData': bookmarkIndex,
                                'JsonRPCAction': {
                                    'method': 'Wox.ChangeQuery',
                                    'parameters': ['bm ' + url, True],
                                    "doNotHideAfterAction".replace('oNo', 'on'): True
                                }
                            }
                        )
                elif type == 'bookmark':
                    if bookmark['iconId'] != 0:
                        iconPath = './Images/iconId{}.png'.format(bookmark['iconId'])
                    else:
                    	if(TargetPlatform == "Chrome"):
                    		iconPath = './Images/chromeIcon.png'
                    	elif(TargetPlatform == "Edge"):
                    		iconPath = './Images/edgeIcon.png'
                    result.append(
                        {
                            'Title': title,
                            'SubTitle': url,
                            'IcoPath': iconPath,
                            'ContextData': bookmarkIndex,
                            'JsonRPCAction': {
                                'method': 'openUrl',
                                'parameters': [url],
                                "doNotHideAfterAction".replace('oNo', 'on'): False
                            }
                        }
                    )
        return result

    def context_menu(self, bookmarkIndex):
        bookmark = self.bookmarkList[bookmarkIndex]
        url = bookmark['url']
        title = bookmark['title']
        path = bookmark['path']
        if bookmark['iconId'] != 0:
            iconPath = './Images/iconId{}.png'.format(bookmark['iconId'])
        else:
            if bookmark['type'] != 'folder':
            	if(TargetPlatform == "Chrome"):
            		iconPath = './Images/chromeIcon.png'
            	elif(TargetPlatform == "Edge"):
            		iconPath = './Images/edgeIcon.png'
            else:
                iconPath = './Images/folderIcon.png'
        results = [
            {
                'Title': 'URL: ' + url,
                'SubTitle': 'Press Enter to Copy URL',
                'IcoPath': iconPath,
                'JsonRPCAction': {
                    'method': 'copyData',
                    'parameters': [url],
                    "doNotHideAfterAction".replace('oNo', 'on'): False,
                }
            }, {
                'Title': 'Title: ' + title,
                'SubTitle': 'Press Enter to Copy Title',
                'IcoPath': iconPath,
                'JsonRPCAction': {
                    'method': 'copyData',
                    'parameters': [title],
                    "doNotHideAfterAction".replace('oNo', 'on'): False,
                }
            }, {
                'Title': 'Path: ' + path,
                'SubTitle': 'Press Enter to Copy Path',
                'IcoPath': iconPath,
                'JsonRPCAction': {
                    'method': 'copyData',
                    'parameters': [path],
                    "doNotHideAfterAction".replace('oNo', 'on'): False,
                }
            }
        ]
        return results

    @classmethod
    def openUrl(cls, url):
        webbrowser.open(url)

    @classmethod
    def copyData(cls, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
        win32clipboard.CloseClipboard()


if __name__ == '__main__':
    getBookmarks()
