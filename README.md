# Wox.Plugin.ChromeBookmarks
PS: To Change Platform(current supported: Chrome and Chromium Edge), please chang the value of TargetPlatform in <main.py:14>

Other Chromium browser should be available too: by adding the bookmark path manually (see: self.__dataPath__ , or just search TargetPlatform in the main.py to find all codes supporting muti-platform)

In the Browser Appdata, there should be 3 data file needed for loading the cache: Favicons (website icons), History (historys), Bookmarks (bookmark data)

In which History is not needed in this plugin (it's for another plugin: https://github.com/wayneferdon/Wox.Plugin.ChromeHistory )
