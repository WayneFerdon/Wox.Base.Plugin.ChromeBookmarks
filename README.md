# Wox.Plugin.ChromeBookmarks
1. To Change Platform(current supported: Chrome and Chromium Edge), please chang the value of [main.py: Line15: TargetPlatform](https://github.com/wayneferdon/Wox.Plugin.ChromeBookmarks/blob/master/main.py#L15)

2. Other Chromium browser should be available too: by adding the bookmark path manually, or just search TargetPlatform in the main.py to find all codes supporting muti-platform)
>see: [main.py: Line37: self.__dataPath__](https://github.com/wayneferdon/Wox.Plugin.ChromeBookmarks/blob/master/main.py#L73) 

3. In the Browser Appdata, there should be 3 data file needed for loading the cache: Favicons (website icons), History (historys), Bookmarks (bookmark data). In which History is not needed in this plugin
> it's for another plugin: https://github.com/wayneferdon/Wox.Plugin.ChromeHistory )
