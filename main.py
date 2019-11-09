# -*- coding: utf-8 -*-
# require pypiwin32, can be install by pip
from wox import Wox, WoxAPI
import re
import webbrowser
import json
import os
import win32con
import win32clipboard

def makeList(itemsList, childItems, pathFolder):
    for item in childItems:
        if 'children' in item.keys():
            if item['type'] == 'folder':
                folderName = item['name']
                childPathFolder = pathFolder + '/' + folderName
                subItem = {
                    'title': folderName,
                    'url': childPathFolder,
                    'path': pathFolder,
                    'type': 'folder'
                }
                itemsList.append(subItem)
                itemsList = makeList(itemsList, item['children'], childPathFolder)
        else:
            subItem = {
                'title': item['name'],
                'url': item['url'],
                'path': pathFolder,
                'type': 'bookmark'
            }
            itemsList.append(subItem)
    return itemsList


class getBookmarks(Wox):
    filePath = os.environ['LOCALAPPDATA'] + r'\Google\Chrome\User Data\Default\Bookmarks'

    with open(filePath, 'r', encoding='UTF-8') as f:
        data = json.load(f)

    bookmarkList = []
    listKey = []
    for key in data['roots']:
        listKey.append(key)

    j = 0
    for root in listKey:
        if j != 2:
            childItems = data['roots'][listKey[j]]['children']
            bookmarkList = makeList(bookmarkList, childItems, root)
        j += 1

    def query(self, queryString):
        urlIcon = 'Images/chrome-logo.png'
        folderIcon = 'Images/folder.png'
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
                    if url == queryString:
                        result.insert(0, {
                                'Title': 'Parent:' + path,
                                'SubTitle': 'Press Enter to Return to Parent Folder',
                                'IcoPath': folderIcon,
                                'ContextData': bookmarkIndex,
                                'JsonRPCAction': {
                                    'method': 'Wox.ChangeQuery',
                                    'parameters': ['bm ' + path, True],
                                    'dontHideAfterAction': True
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
                                    'dontHideAfterAction': True
                                }
                            }
                        )
                elif type == 'bookmark':
                    result.append(
                        {
                            'Title': title,
                            'SubTitle': url,
                            'IcoPath': urlIcon,
                            'ContextData': bookmarkIndex,
                            'JsonRPCAction': {
                                'method': 'openUrl',
                                'parameters': [url],
                                'dontHideAfterAction': False
                            }
                        }
                    )
        return result

    def context_menu(self, bookmarkIndex):
        bookmark = self.bookmarkList[bookmarkIndex]
        url = bookmark['url']
        title = bookmark['title']
        path = bookmark['path']
        logo = 'Images/chrome-logo.png'
        results = [{
            'Title': 'URL: ' + url,
            'SubTitle': 'Press Enter to Copy URL',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [url],
                'dontHideAfterAction': False,
            }
        }, {
            'Title': 'Title: ' + title,
            'SubTitle': 'Press Enter to Copy Title',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [title],
                'dontHideAfterAction': False,
            }
        }, {
            'Title': 'Path: ' + path,
            'SubTitle': 'Press Enter to Copy Path',
            'IcoPath': logo,
            'JsonRPCAction': {
                'method': 'copyData',
                'parameters': [path],
                'dontHideAfterAction': False,
            }
        }]
        return results

    def openUrl(self, url):
        webbrowser.open(url)

    def copyData(self, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
        win32clipboard.CloseClipboard()


if __name__ == '__main__':
    getBookmarks()
