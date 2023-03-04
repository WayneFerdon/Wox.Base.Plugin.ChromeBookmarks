# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 17:07:35
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-03-04 13:55:43
# FilePath: \Flow.Launcher.Plugin.ChromeBookmarks\ChromeQuery.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import webbrowser
from ChromeCache import *
from RegexList import *
from Query import *

TargetPlatform = Platform.Chrome # Chrome, Edge

class ChromeQuery(Query):
    Cache(TargetPlatform)
    _datas_ = list[ChromeData]()

    def _getDatas_(self) -> list[ChromeData]:
        return None

    def _getResult_(self, regex:RegexList, data:ChromeData):
        return None

    def _extraContextMenu_(self, data:ChromeData, iconPath:str):
        return []

    def query(self, queryString:str):
        results = list()
        regex = RegexList(queryString)
        self._datas_ = self._getDatas_()
        for data in self._datas_:
            result = self._getResult_(regex, data)
            if result is None:
                continue
            results.append(result)
        return results

    def context_menu(self, index:int):
        self.query('')
        data = self._datas_[index]

        results = [
            self.getCopyDataResult('URL', data.url, data.icon), 
            self.getCopyDataResult('Title', data.title, data.icon)
        ]
        results += self._extraContextMenu_(data)
        return results

    @classmethod
    def _openUrl_(cls, url:str):
        webbrowser.open(url)