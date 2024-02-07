import threading
import resources.lib.logging as logging
from resources.lib.monitoring import Monitor
from resources.lib.player import Player
from resources.lib.task_handling import TaskHandlerFactory


class TaskManagerAbortException(BaseException):
    pass


class TaskManager(threading.Thread):
    DEBOUNCE_WAIT = 1

    def __init__(self, monitor: Monitor):
        super().__init__()
        self.logger = logging.getLogger(self)
        self.player = Player()
        self.player.onPlayBackStoppedCallBack = self._onPlaybackStopped
        self.tasks = TaskQueue()
        self.tasksLock = threading.Condition()
        self.taskHandlerFactory = TaskHandlerFactory(monitor)
        self.stopRequested = False
        self.debounceTimer = None

    def __enter__(self):
        self.start()

        return self

    def __exit__(self, *args):
        # Should be true only of the thread hasn't been started
        if not self.is_alive():
            return

        self.logger.info("Stopping...")
        self._stop()
        self.join()
        self.logger.info("Stopped.")

    def clear(self):
        with self.tasksLock:
            self.tasks.clear()

    def add(self, task):
        def timerCallback():
            with self.tasksLock:
                # Notify the lock to check the waiting condition, as new task
                # has been added.
                self.tasksLock.notify()

        with self.tasksLock:
            if self.debounceTimer is not None:
                self.debounceTimer.cancel()
            self.tasks.append(task)
            self._logTaskQueueSize()

        # Start debounce timer, which will notify the condition lock about added task,
        # if it doesn't get cancelled by addition of a new task.
        self.debounceTimer = threading.Timer(self.DEBOUNCE_WAIT, timerCallback)
        self.debounceTimer.start()

    def run(self):
        while True:
            try:
                task = self._get()
            except TaskManagerAbortException:
                break

            self.logger.debug("Starting task: %s." % task)
            self._logTaskQueueSize()

            handler = self.taskHandlerFactory.getHandler(task)
            handler.execute()

            self.logger.debug("Finished task: %s." % task)
            self._logTaskQueueSize()

    def _stop(self):
        with self.tasksLock:
            self.stopRequested = True
            # Notify the lock to check the waiting condition, as stop
            # has been initiated.
            self.tasksLock.notify()

    def _get(self):
        """
        Removes and returns an item from the task queue. If the queue is empty,
        will block the thread and wait until there is an item in the queue.
        """

        with self.tasksLock:
            while self._needToWait():
                self.tasksLock.wait()

            if self.stopRequested:
                raise TaskManagerAbortException()

            task = self.tasks.pop()
            self._logTaskQueueSize()
            return task

    def _needToWait(self) -> bool:
        if self.stopRequested:
            self.logger.debug("Stop requested. Not waiting anymore for new tasks.")
            return False

        if self.player.isPlaying():
            self.logger.debug("Waiting for playback to stop.")
            return True

        if self.tasks.size() == 0:
            self.logger.debug("Waiting for new tasks.")
            return True

        return False

    def _onPlaybackStopped(self):
        with self.tasksLock:
            self.logger.debug("Playback stopped.")
            # Notify the lock to check the waiting condition, as playback
            # has be stopped.
            self.tasksLock.notify()

    def _logTaskQueueSize(self):
        self.logger.debug("Task queue size: %i." % self.tasks.size())


class TaskQueue:
    """
    Ordered queue that doesn't allow duplicates
    """

    def __init__(self):
        self.logger = logging.getLogger(self)
        self.tasks = []

    def append(self, task):
        if task in self.tasks:
            self.logger.debug("Task skipped, as it's already in the queue: %s." % task)
            return

        self.tasks.append(task)
        self.logger.debug("Task added: %s." % task)

    def pop(self):
        task = self.tasks.pop(0)
        self.logger.debug("Task popped: %s." % task)
        return task

    def clear(self):
        self.tasks.clear()
        self.logger.debug("All tasks cleared.")

    def size(self):
        return len(self.tasks)
