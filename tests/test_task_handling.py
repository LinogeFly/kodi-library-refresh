import threading
import unittest
import xbmc
import time
from threading import Thread
from resources.lib.monitoring import Monitor
import resources.lib.tasks as tasks
from unittest.mock import MagicMock, patch
from resources.lib.task_handling import CleanLibraryTaskHandler, UpdateLibraryTaskHandler
from resources.lib.library import MediaSource, MediaType


class CleanLibraryTaskHandler_Execute_TestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch.object(xbmc, "executebuiltin")
    def test_executesKodiBuiltInFunction_whenCalled(self, mock: MagicMock):
        # Arrange
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.CleanLibrary(mediaSource)
        sut = CleanLibraryTaskHandler(task, monitor)
        sutThread = Thread(target=lambda: sut.execute())

        # Act
        sutThread.start()
        monitor.onCleanStarted("video")
        monitor.onCleanFinished("video")
        sutThread.join()

        # Assert
        mock.assert_called_once_with("cleanlibrary(video)")

    def test_waitsUntilLibraryCleanGetsStarted_afterExecutingKodiBuiltInFunction(self):
        # Arrange
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.CleanLibrary(mediaSource)
        sut = CleanLibraryTaskHandler(task, monitor)
        sutThread = Thread(target=lambda: sut.execute())

        # Act
        start = time.time()
        sutThread.start()
        time.sleep(0.1)
        monitor.onCleanStarted("video")
        monitor.onCleanFinished("video")
        sutThread.join()
        sutExecutionTime = time.time() - start

        # Assert
        self.assertAlmostEqual(sutExecutionTime, 0.1, places=1)

    def test_waitsUntilLibraryCleanGetsFinished_afterExecutingKodiBuiltInFunction(self):
        # Arrange
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.CleanLibrary(mediaSource)
        sut = CleanLibraryTaskHandler(task, monitor)
        sutThread = Thread(target=lambda: sut.execute())

        # Act
        start = time.time()
        sutThread.start()
        time.sleep(0.1)
        monitor.onCleanStarted("video")
        time.sleep(0.2)
        monitor.onCleanFinished("video")
        sutThread.join()
        sutExecutionTime = time.time() - start

        # Assert
        self.assertAlmostEqual(sutExecutionTime, 0.3, places=1)

    def test_aborts_ifCleanDoesNotStartBeforeTheTimeOut_afterExecutingKodiBuiltInFunction(self):
        # Arrange
        def sutThreadTarget(monitor):
            start = time.time()
            sut.execute()
            with lock:
                nonlocal sutExecutionTime
                sutExecutionTime = time.time() - start

        sutExecutionTime = 0
        lock = threading.Lock()
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.CleanLibrary(mediaSource)
        sut = CleanLibraryTaskHandler(task, monitor)
        sut.WAIT_TO_START_TIMEOUT = 0.1
        sutThread = Thread(target=sutThreadTarget, args=(monitor,))

        # Act
        sutThread.start()
        time.sleep(0.2)
        monitor.onCleanStarted("video")
        monitor.onCleanFinished("video")
        sutThread.join()

        # Assert
        self.assertAlmostEqual(sutExecutionTime, 0.1, places=1)


class UpdateLibraryTaskHandler_Execute_TestCase(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    @patch.object(xbmc, "executebuiltin")
    def test_executesKodiBuiltInFunction_whenCalled(self, mock: MagicMock):
        # Arrange
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.UpdateLibrary(mediaSource)
        sut = UpdateLibraryTaskHandler(task, monitor)
        sutThread = Thread(target=lambda: sut.execute())

        # Act
        sutThread.start()
        monitor.onScanStarted("video")
        monitor.onScanFinished("video")
        sutThread.join()

        # Assert
        mock.assert_called_once_with("updatelibrary(video)")

    def test_waitsUntilLibraryScanGetsStarted_afterExecutingKodiBuiltInFunction(self):
        # Arrange
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.UpdateLibrary(mediaSource)
        sut = UpdateLibraryTaskHandler(task, monitor)
        sutThread = Thread(target=lambda: sut.execute())

        # Act
        start = time.time()
        sutThread.start()
        time.sleep(0.1)
        monitor.onScanStarted("video")
        monitor.onScanFinished("video")
        sutThread.join()
        sutExecutionTime = time.time() - start

        # Assert
        self.assertAlmostEqual(sutExecutionTime, 0.1, places=1)

    def test_waitsUntilLibraryScanGetsFinished_afterExecutingKodiBuiltInFunction(self):
        # Arrange
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.UpdateLibrary(mediaSource)
        sut = UpdateLibraryTaskHandler(task, monitor)
        sutThread = Thread(target=lambda: sut.execute())

        # Act
        start = time.time()
        sutThread.start()
        time.sleep(0.1)
        monitor.onScanStarted("video")
        time.sleep(0.2)
        monitor.onScanFinished("video")
        sutThread.join()
        sutExecutionTime = time.time() - start

        # Assert
        self.assertAlmostEqual(sutExecutionTime, 0.3, places=1)

    def test_aborts_ifUpdateDoesNotStartBeforeTheTimeOut_afterExecutingKodiBuiltInFunction(self):
        # Arrange
        def sutThreadTarget(monitor):
            start = time.time()
            sut.execute()
            with lock:
                nonlocal sutExecutionTime
                sutExecutionTime = time.time() - start

        sutExecutionTime = 0
        lock = threading.Lock()
        monitor = Monitor()
        mediaSource = MediaSource("/media/movies", MediaType.video)
        task = tasks.UpdateLibrary(mediaSource)
        sut = UpdateLibraryTaskHandler(task, monitor)
        sut.WAIT_TO_START_TIMEOUT = 0.1
        sutThread = Thread(target=sutThreadTarget, args=(monitor,))

        # Act
        sutThread.start()
        time.sleep(0.2)
        monitor.onScanStarted("video")
        monitor.onScanFinished("video")
        sutThread.join()

        # Assert
        self.assertAlmostEqual(sutExecutionTime, 0.1, places=1)
