import xbmcaddon
import xbmc
import resources.lib.logging as logging


class Settings(xbmc.Monitor):
    def __init__(self, onChange: None):
        super().__init__()
        self.logger = logging.getLogger(self)
        self.onUpdate = onChange
        # Cached settings. Get reloaded in onSettingsChanged call back function.
        self.settings = xbmcaddon.Addon().getSettings()

    def isRefreshVideoEnabled(self):
        return self.settings.getBool("refresh_video")

    def isRefreshMusicEnabled(self):
        return self.settings.getBool("refresh_music")

    @logging.notifyOnError
    def onSettingsChanged(self):
        self.logger.debug("Settings changed.")

        # Reload the settings
        self.settings = xbmcaddon.Addon().getSettings()
        self.logger.debug("Settings re-cached.")

        if self.onUpdate is not None:
            self.onUpdate()
