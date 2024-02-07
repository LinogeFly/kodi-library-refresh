from enum import Enum
import xbmc
import resources.lib.logging as logging


class Event(Enum):
    onScanStarted = 1
    onScanFinished = 2
    onCleanStarted = 3
    onCleanFinished = 4


class Monitor(xbmc.Monitor):
    def __init__(self) -> None:
        super().__init__()
        self.logger = logging.getLogger(self)

        # Key is monitor event type, value is an array for callback functions
        self.eventCallbacks = {
            Event.onScanStarted: [],
            Event.onScanFinished: [],
            Event.onCleanStarted: [],
            Event.onCleanFinished: [],
        }

    def attach(self, event: Event, callback):
        callbacks = self.eventCallbacks[event]
        callbacks.append(callback)
        if len(callbacks) > 1:
            raise Exception(f"Multiple event handlers detected for '{event}'.")

    def detach(self, event: Event, callback):
        callbacks = self.eventCallbacks[event]
        callbacks.remove(callback)
        if len(callbacks) > 0:
            raise Exception(f"Multiple event handlers detected for '{event}'.")

    @logging.notifyOnError
    def onScanStarted(self, *args) -> None:
        for cb in self.eventCallbacks[Event.onScanStarted]:
            cb()

    @logging.notifyOnError
    def onScanFinished(self, *args) -> None:
        for cb in self.eventCallbacks[Event.onScanFinished]:
            cb()

    @logging.notifyOnError
    def onCleanStarted(self, *args) -> None:
        for cb in self.eventCallbacks[Event.onCleanStarted]:
            cb()

    @logging.notifyOnError
    def onCleanFinished(self, *args) -> None:
        for cb in self.eventCallbacks[Event.onCleanFinished]:
            cb()
