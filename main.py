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


class getBookmarks(Wox):
# class getBookmarks():
    filePath = os.environ['localAppData'.upper()] + '/Google/Chrome/User Data/Default/Bookmarks'
    localAppData = os.environ['localAppData'.upper()]
    dataPath = localAppData + '/Google/Chrome/User Data/Default'
    favIcons = dataPath + '/Favicons'
    favIconsToRead = dataPath + '/FaviconsToRead'
    shutil.copyfile(favIcons, favIconsToRead)

    # <editor-fold desc="connect to database copy">
    favIconsCursor = sqlite3.connect(favIconsToRead).cursor()
    # </editor-fold>

    # <editor-fold desc="create icon image temps">
    favIconBitmapSelectStatement = 'SELECT icon_id, image_data, width, height FROM favicon_bitmaps'
    favIconsCursor.execute(favIconBitmapSelectStatement)
    favIconBitmapCursorResults = favIconsCursor.fetchall()
    favIconBitmapInfoList = []
    favIconBitmapIdList = []
    for iconId, imageData, width, height in favIconBitmapCursorResults:
        if iconId in favIconBitmapIdList:
            iconIdIndex = favIconBitmapIdList.index(iconId)
            if width < favIconBitmapInfoList[iconIdIndex][0] or height < favIconBitmapInfoList[iconIdIndex][1]:
                continue
        with open('./Images/iconId{}.png'.format(iconId), 'wb') as f:
            f.write(imageData)
        favIconBitmapIdList.append(iconId)
        favIconBitmapInfoList.append([width, height])
    # </editor-fold>

    # <editor-fold desc="get url icon id"
    favIconsSelectStatement = 'SELECT page_url, icon_id FROM icon_mapping'
    favIconsCursor.execute(favIconsSelectStatement)
    favIconsCursorResults = favIconsCursor.fetchall()
    netLocationIconList = []
    netLocationList = []
    for url, iconId in favIconsCursorResults:
        netLocation = urlparse(url).netloc
        if netLocation in netLocationList:
            continue
        netLocationList.append(netLocation)
        netLocationIconList.append(iconId)
    # </editor-fold>

    favIconsCursor.close()

    with open(filePath, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    bookmarkList = []
    for rootKey in data['roots']:
        root = data['roots'][rootKey]
        try:
            childItems = root['children']
        except BaseException:
            continue
        bookmarkList = makeList(bookmarkList, childItems, rootKey)

    for index in range(len(bookmarkList)):
        url = bookmarkList[index]['url']
        netLocation = urlparse(url).netloc
        if netLocation in netLocationList:
            netLocationIndex = netLocationList.index(netLocation)
            bookmarkList[index]['iconId'] = netLocationIconList[netLocationIndex]
        else:
            bookmarkList[index]['iconId'] = 0
    # print(bookmarkList)

    def query(self, queryString):
        urlIcon = './Images/chromeIcon.png'
        folderIcon = './Images/folderIcon.png'
        result = []
        bookmarkList = self.bookmarkList

        queryStringLower = queryString.lower()
        queryList = queryStringLower.split()
        regexList = []
        for query in queryList:
            # pattern = '.*?'.join(query)
            # regexList.append(re.compile(pattern))
            regexList.append(re.compile(query))

        for bookmark in bookmarkList:
            title = bookmark['title']
            url = bookmark['url']
            path = bookmark['path']
            item = title + url + path
            match = True
            for regex in regexList:
                match = regex.search(item.lower()) and match
            if match:
                bookmarkIndex = bookmarkList.index(bookmark)
                type = bookmark['type']
                if type == 'folder':
                    if url in queryString:  # if already in target folder
                        result.insert(0, {
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
                        iconPath = './Images/chromeIcon.png'
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
                iconPath = './Images/chromeIcon.png'
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
