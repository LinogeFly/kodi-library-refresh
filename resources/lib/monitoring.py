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

        # Key is the event type, value is an array for callback functions
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
            self.logger.warn(f"Multiple event handlers detected for '{event}'.")

    def detach(self, event: Event, callback):
        callbacks = self.eventCallbacks[event]
        callbacks.remove(callback)
        if len(callbacks) > 0:
            self.logger.warn(f"Multiple event handlers detected for '{event}'.")

    @logging.notifyOnError
    def onScanStarted(self, *args) -> None:
        self.logger.debug("Scan started.")
        for cb in self.eventCallbacks[Event.onScanStarted]:
            cb()

    @logging.notifyOnError
    def onScanFinished(self, *args) -> None:
        self.logger.debug("Scan finished.")
        for cb in self.eventCallbacks[Event.onScanFinished]:
            cb()

    @logging.notifyOnError
    def onCleanStarted(self, *args) -> None:
        self.logger.debug("Clean started.")
        for cb in self.eventCallbacks[Event.onCleanStarted]:
            cb()

    @logging.notifyOnError
    def onCleanFinished(self, *args) -> None:
        self.logger.debug("Clean finished.")
        for cb in self.eventCallbacks[Event.onCleanFinished]:
            cb()
