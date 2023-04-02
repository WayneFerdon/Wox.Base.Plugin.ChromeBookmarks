# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-03-04 12:45:55
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-02 13:50:55
# FilePath: \Flow.Launcher.Plugin.ChromeBookmarks\Query.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

# -*- coding: utf-8 -*-
import os
import win32con
import win32clipboard
from enum import Enum

from flowlauncher import FlowLauncher as LauncherBase
# from wox import Wox as LauncherBase

class Launcher(LauncherBase):
    class API(Enum):
        ChangeQuery = 0, # change launcher query
        RestartApp = 1, # restart Launcher
        SaveAppAllSettings = 2, #save all Launcher settings
        CheckForNewUpdate = 3, # check for new Launcher update
        ShellRun = 4, # run shell commands
        CloseApp = 5, # close launcher
        HideApp = 6, # hide launcher
        ShowApp = 7, # show launcher
        ShowMsg = 8, # show messagebox
        GetTranslation = 9, # get translation of current language
        OpenSettingDialog = 10, # open setting dialog
        GetAllPlugins = 11, # get all loaded plugins
        StartLoadingBar = 12, # start loading animation in launcher
        StopLoadingBar = 13, # stop loading animation in launcher
        ReloadAllPluginData = 14, # reload all launcher plugins

    @staticmethod
    def GetSettingPath(PathName:str, isPortableMode:bool = False):
        mode = 'Roaming' if isPortableMode else 'Local'
        return os.environ['localAppData'.upper()] + '/../' + mode +'/' + PathName + '/Settings/Settings.json'

    @staticmethod
    def GetAPIName(api:API):
        return Launcher.Name + '.' + api.name
    
    Name = 'Flow.Launcher' # or: 'Wox'
    PathName = 'FlowLauncher' # or: 'Wox'

    SettingPath = GetSettingPath(PathName)
    if not os.path.isfile(SettingPath):
        SettingPath = GetSettingPath(PathName, True)

class Query(Launcher):
# class Query():
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
        return QueryResult(title, subTitle, iconPath, None, cls.copyData.__name__, True, titleData).toDict()

class QueryResult:
    def __init__(self, title:str, subtitle:str, icon:str, context , method:str, hideAfterAction:bool, *args) -> None:
        self.title = title
        self.subtitle = subtitle
        self.icon = icon
        self.method = method
        self.parameters = args
        self.context = context
        self.hideAfterAction = hideAfterAction
    
    def toDict(self):
        jsonResult = {
            'Title': self.title, 
            'SubTitle': self.subtitle, 
            'IcoPath': self.icon, 
            'ContextData': self.context
        }
        if self.method is not None:
            jsonResult['JsonRPCAction'] = {
                'method': self.method, 
                'parameters': self.parameters, 
                "doNotHideAfterAction".replace('oNo', 'on'): (not self.hideAfterAction), 
            }
        return jsonResult
