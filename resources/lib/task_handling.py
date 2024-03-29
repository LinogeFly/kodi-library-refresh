import threading
import xbmc
from resources.lib.library import InvalidMediaTypeException, MediaType
import resources.lib.logging as logging
import resources.lib.monitoring as monitoring
import resources.lib.tasks as tasks


class TaskHandlerFactory:
    def __init__(self, monitor: monitoring.Monitor):
        self.monitor = monitor

    def getHandler(self, task):
        if type(task) is tasks.CleanLibrary:
            return CleanLibraryTaskHandler(task, self.monitor)
        if type(task) is tasks.UpdateLibrary:
            return UpdateLibraryTaskHandler(task, self.monitor)
        raise NotImplementedError()


class CleanLibraryTaskHandler:
    WAIT_TO_START_TIMEOUT = 5

    def __init__(self, task: tasks.CleanLibrary, monitor: monitoring.Monitor) -> None:
        self.logger = logging.getLogger(self)
        self.task = task
        self.monitor = monitor
        self.startEvent = threading.Event()
        self.finishEvent = threading.Event()

    def execute(self):
        """
        Triggers Kodi command to clean the library. Waits for the clean
        to start first and then waits for it to finish. Blocks the thread
        while waiting.
        """

        self.logger.info("Starting library clean...")

        self.monitor.attach(monitoring.Event.onCleanStarted, self._onStarted)
        self.monitor.attach(monitoring.Event.onCleanFinished, self._onFinished)
        try:
            self._executeKodiCommand()

            self.logger.debug("Waiting for Kodi library clean to start.")
            started = self.startEvent.wait(self.WAIT_TO_START_TIMEOUT)
            if not started:
                self.logger.warn("Waiting for Kodi library clean to start has timed out.")
                return

            # No timeout here for waiting as it can take a pretty long time for the clean
            # to finish. The event should always get raised by Kodi. It's raised when
            # the clean succeeds, fails or if we exit Kodi during the clean.
            self.finishEvent.wait()
        finally:
            self.monitor.detach(monitoring.Event.onCleanStarted, self._onStarted)
            self.monitor.detach(monitoring.Event.onCleanFinished, self._onFinished)

        self.logger.info("Finished library clean.")

    def _onStarted(self):
        self.startEvent.set()

    def _onFinished(self):
        self.finishEvent.set()

    def _executeKodiCommand(self):
        func = "cleanlibrary(%s)" % _getMediaTypeString(self.task.mediaSource.type)
        xbmc.executebuiltin(func)
        self.logger.debug('Called "%s" Kodi built-in function.' % func)


class UpdateLibraryTaskHandler:
    WAIT_TO_START_TIMEOUT = 5

    def __init__(self, task: tasks.UpdateLibrary, monitor: monitoring.Monitor) -> None:
        self.logger = logging.getLogger(self)
        self.task = task
        self.monitor = monitor
        self.startEvent = threading.Event()
        self.finishEvent = threading.Event()

    def execute(self):
        """
        Triggers Kodi command to update the library. Waits for the update
        to start first and then waits for it to finish. Blocks the thread
        while waiting.
        """

        self.logger.info("Starting library scan...")

        self.monitor.attach(monitoring.Event.onScanStarted, self._onStarted)
        self.monitor.attach(monitoring.Event.onScanFinished, self._onFinished)
        try:
            self._executeKodiCommand()

            self.logger.debug("Waiting for Kodi library scan to start.")
            started = self.startEvent.wait(self.WAIT_TO_START_TIMEOUT)
            if not started:
                self.logger.warn("Waiting for Kodi library scan to start has timed out.")
                return

            # No timeout here for waiting as it can take a pretty long time for the scan
            # to finish. The event should always get raised by Kodi. It's raised when
            # the scan succeeds, fails or if we exit Kodi during the scan.
            self.finishEvent.wait()
        finally:
            self.monitor.detach(monitoring.Event.onScanStarted, self._onStarted)
            self.monitor.detach(monitoring.Event.onScanFinished, self._onFinished)

        self.logger.info("Finished library scan.")

    def _onStarted(self):
        self.startEvent.set()

    def _onFinished(self):
        self.finishEvent.set()

    def _executeKodiCommand(self):
        func = "updatelibrary(%s)" % _getMediaTypeString(self.task.mediaSource.type)
        xbmc.executebuiltin(func)
        self.logger.debug('Called "%s" Kodi built-in function.' % func)


def _getMediaTypeString(mediaType: MediaType) -> str:
    """
    Returns string value for media type, that is used when calling
    Kodi library built-in functions.
    """

    if mediaType == MediaType.video:
        return "video"
    if mediaType == MediaType.music:
        return "music"
    raise InvalidMediaTypeException(mediaType)
