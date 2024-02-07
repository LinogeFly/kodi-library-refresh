import xbmc
import resources.lib.logging as logging


class Player(xbmc.Player):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(self)
        self.onPlayBackStoppedCallBack = None

    @logging.notifyOnError
    def onPlayBackStopped(self) -> None:
        self.logger.debug("Playback stopped.")
        if self.onPlayBackStoppedCallBack is not None:
            self.onPlayBackStoppedCallBack()

    @logging.notifyOnError
    def onPlayBackEnded(self) -> None:
        self.logger.debug("Playback ended.")
        if self.onPlayBackStoppedCallBack is not None:
            self.onPlayBackStoppedCallBack()
