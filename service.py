import threading
import resources.lib.logging as logging
from resources.lib.library import Library
from resources.lib.settings import Settings
from resources.lib.monitoring import Monitor
from resources.lib.watcher import Watcher
from resources.lib.task_management import TaskManager


def main():
    logger = logging.getLogger(__name__)

    # And event handler for add-on settings changes. If the settings
    # change we re-create file system watchers to be sure those are
    # created with the latest add-on settings.
    def _onSettingsChange():
        watcher.clear()
        taskManager.clear()
        watcher.watch(library.getMediaSources())

    # Handle uncaught exceptions raised by other than the main threads
    # in order to show an error notification in the UI, as those
    # exceptions are not caught in the main thread and will go
    # unnoticed otherwise
    def _threadingExceptionHandler(args):
        logging.notifyError()
        raise

    logger.info("Starting...")
    threading.excepthook = _threadingExceptionHandler
    monitor = Monitor()

    with TaskManager(monitor) as taskManager, Watcher(taskManager) as watcher:
        settings = Settings(_onSettingsChange)
        library = Library(settings)
        watcher.watch(library.getMediaSources())
        logger.info("Started.")
        monitor.waitForAbort()

    logger.info("Stopped.")


if __name__ == "__main__":
    main()
