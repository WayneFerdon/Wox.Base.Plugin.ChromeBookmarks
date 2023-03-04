<!--
 * @Author: WayneFerdon wayneferdon@hotmail.com
 * @Date: 2023-03-04 12:45:55
 * @LastEditors: WayneFerdon wayneferdon@hotmail.com
 * @LastEditTime: 2023-03-04 23:15:29
 * @FilePath: \undefinedc:\Users\WayneFerdon\AppData\Local\FlowLauncher\app-1.14.0\Plugins\Flow.Launcher.Plugin.ChromeBookmarks\README.md
 * ----------------------------------------------------------------
 * Copyright (c) 2023 by Wayne Ferdon Studio. All rights reserved.
 * Licensed to the .NET Foundation under one or more agreements.
 * The .NET Foundation licenses this file to you under the MIT license.
 * See the LICENSE file in the project root for more information.
-->
# Wox.Plugin.ChromeBookmarks

1. To Change Platform(current supported: Chrome and Chromium Edge), please chang the value of [ChromeQuery.py: Line19: TargetPlatform](https://github.com/WayneFerdon/Wox.Plugin.ChromeBookmarks/blob/master/ChromeQuery.py#L19)

2. Other Chromium browser should be available too: by adding the bookmark path manually, or just search TargetPlatform in the main.py to find all codes supporting muti-platform)
>see: [ChromeCache.py: Line139: \_\_setPlatform__(TargetPlatform)](https://github.com/WayneFerdon/Wox.Plugin.ChromeBookmarks/blob/master/ChromeCache.py#L139)

3. In the Browser Appdata, there should be 3 data file needed for loading the cache: Favicons (website icons), History (historys), Bookmarks (bookmark data). In which History is not needed in this plugin
> it's for another plugin: https://github.com/wayneferdon/Wox.Plugin.ChromeHistory )

4. To Change from flow launcher to legacy Wox launcher
