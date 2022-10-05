# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 17:07:35
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-05 17:58:06
# FilePath: \Wox.Plugin.ChromeBookmarks\ChromeWox.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import os
import webbrowser
from ChromeCache import *
from RegexList import *
from WoxQuery import *

TargetPlatform = Platform.Chrome # Chrome, Edge

class ChromeWox(WoxQuery):
    cache = Cache(TargetPlatform)
    PlatformIcon = cache.PlatformIcon
    datas = list[ChromeData]()

    def getDatas(self) -> list[ChromeData]:
        return None

    def getResult(self, regex:RegexList, data:ChromeData):
        return None

    def extraContextMenu(self, data:ChromeData, iconPath:str):
        return []

    def query(self, queryString:str):
        results = list()
        regex = RegexList(queryString)
        self.datas = self.getDatas()()
        for data in self.datas:
            result = self.getResult(regex, data)
            if result is None:
                continue
            results.append(result)
        return results

    def context_menu(self, index:int):
        self.query('')
        data = self.datas[index]
        url = data.url
        title = data.title

        if data.iconID != 0:
            iconPath = './Images/icon{}.png'.format(data.iconID)
        else:
            iconPath = self.PlatformIcon
        iconPath = os.path.join(os.path.abspath('./'),iconPath)
        
        results = [
            self.getCopyDataResult('URL', url, iconPath), 
            self.getCopyDataResult('Title', title, iconPath)
        ]
        results += self.extraContextMenu(data, iconPath)
        return results

    @classmethod
    def openUrl(cls, url:str):
        webbrowser.open(url)