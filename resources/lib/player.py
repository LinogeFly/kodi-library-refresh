import xbmc
import resources.lib.logging as logging
from enum import Enum


class Event(Enum):
    onPlayBackFinished = 1  # Handles both "stopped" and "ended" events


class Player(xbmc.Player):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(self)

        # Key is the event type, value is an array for callback functions
        self.eventCallbacks = {
            Event.onPlayBackFinished: [],
        }

    def attach(self, event: Event, callback):
        callbacks = self.eventCallbacks[event]
        callbacks.append(callback)
        if len(callbacks) > 1:
            self.logger.warn(f"Multiple event handlers detected for '{event}'.")

    def detach(self, event: Event, callback):
        callbacks = self.eventCallbacks[event]
        callbacks.remove(callback)
        if len(callbacks) > 0:
            self.logger.warn(f"Multiple event handlers detected for '{event}'.")

    @logging.notifyOnError
    def onPlayBackStopped(self) -> None:
        self.logger.debug("Playback stopped.")
        for cb in self.eventCallbacks[Event.onPlayBackFinished]:
            cb()

    @logging.notifyOnError
    def onPlayBackEnded(self) -> None:
        self.logger.debug("Playback ended.")
        for cb in self.eventCallbacks[Event.onPlayBackFinished]:
            cb()
