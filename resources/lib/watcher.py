import sys
import threading
import xbmc
from typing import List
import resources.lib.logging as logging
import resources.lib.task_management as task_management
import resources.lib.tasks as tasks
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent, FileSystemMovedEvent
from resources.lib.library import MediaSource, MediaType, InvalidMediaTypeException
from resources.lib.util.file_system import getFileExt, isHidden


class EventHandler(FileSystemEventHandler):
    def __init__(self, taskManager: task_management.TaskManager, mediaSource: MediaSource):
        super().__init__()
        self.logger = logging.getLogger(self)
        self.taskManager = taskManager
        self.mediaSource = mediaSource

    def on_any_event(self, event: FileSystemEvent):
        self.logger.debug('File system event: <%s> for "%s".' % (event.event_type, event.src_path))

    def on_created(self, event: FileSystemEvent):
        if event.is_directory:
            self._logDirectorySkip(event)
            return
        if self._isNotSupportedExtension(event.src_path):
            self._logNotSupportedSkip(event, event.src_path)
            return
        if self._isHidden(event.src_path):
            self._logHiddenSkip(event, event.src_path)
            return

        self.taskManager.add(tasks.UpdateLibrary(self.mediaSource))

    def on_deleted(self, event: FileSystemEvent):
        if self._shouldSkipDelete(event):
            return

        self.taskManager.add(tasks.CleanLibrary(self.mediaSource))

    def on_moved(self, event: FileSystemMovedEvent):
        if event.is_directory:
            self._logDirectorySkip(event)
            return
        if self._isNotSupportedExtension(event.src_path):
            self._logNotSupportedSkip(event, event.src_path)
            return
        if self._isHidden(event.src_path) and not self._isHidden(event.dest_path):
            self.taskManager.add(tasks.UpdateLibrary(self.mediaSource))
            return
        if self._isHidden(event.dest_path) and not self._isHidden(event.src_path):
            self.taskManager.add(tasks.CleanLibrary(self.mediaSource))
            return
        if self._isHidden(event.dest_path):
            self._logHiddenSkip(event, event.dest_path)
            return

        self.taskManager.add(tasks.UpdateLibrary(self.mediaSource))
        self.taskManager.add(tasks.CleanLibrary(self.mediaSource))

    def _shouldSkipDelete(self, event: FileSystemEvent):
        if sys.platform.startswith("win"):
            return self._shouldSkipDeleteOnWindows(event)

        return self._shouldSkipDeleteDefault(event)

    def _shouldSkipDeleteDefault(self, event: FileSystemEvent):
        if event.is_directory:
            self._logDirectorySkip(event)
            return True
        if self._isNotSupportedExtension(event.src_path):
            self._logNotSupportedSkip(event, event.src_path)
            return True
        if self._isHidden(event.src_path):
            self._logHiddenSkip(event, event.src_path)
            return True

        return False

    def _shouldSkipDeleteOnWindows(self, event: FileSystemEvent):
        if self._isHidden(event.src_path):
            self._logHiddenSkip(event, event.src_path)
            return True
        if getFileExt(event.src_path) == "":
            return False
        if self._isNotSupportedExtension(event.src_path):
            self._logNotSupportedSkip(event, event.src_path)
            return True

        return False

    def _isHidden(self, path):
        return isHidden(self.mediaSource.path, path)

    def _isNotSupportedExtension(self, path: str):
        return getFileExt(path) not in _getSupportedExtensions(self.mediaSource.type)

    def _logDirectorySkip(self, event: FileSystemEvent):
        self.logger.debug('Skip <%s> event for "%s" because it\'s a directory.' % (event.event_type, event.src_path))

    def _logNotSupportedSkip(self, event: FileSystemEvent, path: str):
        self.logger.debug(
            'Skip <%s> event for "%s" because its media type is not supported.' % (event.event_type, path)
        )

    def _logHiddenSkip(self, event: FileSystemEvent, path: str):
        self.logger.debug(
            'Skip <%s> event for "%s" because it\'s hidden or located in a hidden directory.'
            % (event.event_type, path)
        )


class Watcher:
    def __init__(self, taskManager: task_management.TaskManager):
        self.logger = logging.getLogger(self)
        self.taskManager = taskManager
        self.observer = Observer()
        self.started = threading.Event()

    def __enter__(self):
        self.observer.start()
        self.started.set()

        return self

    def __exit__(self, *args):
        if not self.started.is_set():
            return

        self.logger.info("Stopping...")
        self.observer.stop()
        self.observer.join()
        self.logger.info("Stopped.")

    def watch(self, mediaSources):
        # Making sure the observer has been started before creating any watchers.
        # This is needed to prevent the watch fail as a whole in case of some
        # invalid media sources. We want to create one watcher for a given media
        # source at a time. In a case when a media source has an invalid path,
        # the watcher creation is skipped for that media source and we proceed
        # with the the rest of the media sources.
        if not self.started.is_set():
            raise Exception("Observer is not running. It needs to be started before adding watchers.")

        for mediaSource in mediaSources:
            eventHandler = EventHandler(self.taskManager, mediaSource)
            try:
                self.observer.schedule(eventHandler, mediaSource.path, recursive=True)
                self.logger.info('Watching "%s".' % mediaSource.path)
            except OSError:
                self.logger.warn('Failed to watch "%s".' % mediaSource.path)
                logging.notifyWarning("Unable to watch some media sources.")

    def clear(self):
        self.observer.unschedule_all()
        self.logger.info("All watchers cleared.")


def _getSupportedExtensions(mediaType: MediaType) -> List[str]:
    response = ""
    if mediaType == MediaType.video:
        response = xbmc.getSupportedMedia("video")
    elif mediaType == MediaType.music:
        response = xbmc.getSupportedMedia("music")
    else:
        raise InvalidMediaTypeException(mediaType)

    return response.strip("|").split("|")
