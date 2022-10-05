# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:16:00
# LastEditors: wayneferdon wayneferdon@hotmail.com
# LastEditTime: 2022-10-05 17:57:53
# FilePath: \Wox.Plugin.ChromeBookmarks\WoxQuery.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
from wox import Wox, WoxAPI
import win32con
import win32clipboard

class WoxQuery(Wox):
# class WoxQuery():
    @classmethod
    def copyData(cls, data):
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32con.CF_UNICODETEXT, data)
        win32clipboard.CloseClipboard()
    
    @classmethod
    def getCopyDataResult(cls, type, titleData, iconPath) -> dict:
        title = type + ": " + titleData
        subTitle = 'Press Enter to Copy ' + type
        return WoxResult(title, subTitle, iconPath, None, cls.copyData.__name__, True, titleData).toDict()

class WoxResult:
    def __init__(self, title:str, subTitle:str, icoPath:str, contextData , method:str, hideAfterAction:bool, *args) -> None:
        self.title = title
        self.subTitle = subTitle
        self.icoPath = icoPath
        self.method = method
        self.parameters = args
        self.contextData = contextData
        self.hideAfterAction = hideAfterAction
    
    def toDict(self):
        jsonResult = {
            'Title': self.title, 
            'SubTitle': self.subTitle, 
            'IcoPath': self.icoPath, 
            'ContextData': self.contextData
        }
        if self.method is not None:
            jsonResult['JsonRPCAction'] = {
                'method': self.method, 
                'parameters': self.parameters, 
                "doNotHideAfterAction".replace('oNo', 'on'): (not self.hideAfterAction), 
            }
        return jsonResult
