# ----------------------------------------------------------------
# Author: wayneferdon wayneferdon@hotmail.com
# Date: 2022-10-05 16:16:00
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-02 12:09:08
# FilePath: \Flow.Launcher.Plugin.ChromeHistory\Query.py
# ----------------------------------------------------------------
# Copyright (c) 2022 by Wayne Ferdon Studio. All rights reserved.
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

class QueryDebug:
    # 静态变量
    Instance=None
    _flag=False
    def __new__(cls, *args, **kwargs):
        if cls.Instance is None:
            cls.Instance=super().__new__(cls)
        return cls.Instance
    def __init__(self):
        if QueryDebug._flag:
            return
        QueryDebug._flag=True

    Logs = list[str]()
    
    @staticmethod
    def Log(*info):
        QueryDebug.Instance.Logs.append([len(QueryDebug.Instance.Logs), str(list(info))[1:-1] + "\n" + "\n".join(traceback.format_stack())])
