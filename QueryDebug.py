# ----------------------------------------------------------------
# Author: WayneFerdon wayneferdon@hotmail.com
# Date: 2023-04-02 12:21:06
# LastEditors: WayneFerdon wayneferdon@hotmail.com
# LastEditTime: 2023-04-02 12:25:22
# FilePath: \Flow.Launcher.Plugin.ChromeBookmarks\QueryDebug.py
# ----------------------------------------------------------------
# Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
# Licensed to the .NET Foundation under one or more agreements.
# The .NET Foundation licenses this file to you under the MIT license.
# See the LICENSE file in the project root for more information.
# ----------------------------------------------------------------

import traceback
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