import os
import threading
import time
import unittest
from unittest.mock import patch
import resources.lib.tasks as tasks
from resources.lib.library import MediaSource, MediaType
from resources.lib.watcher import EventHandler, Watcher
from tests.support import Waiter
from tests.test_watcher.support import WatcherTestCaseBase


class Watcher_Start_TestCase(WatcherTestCaseBase, unittest.TestCase):
    def test_watchesForChangesInExistingMediaSources_whenBothExistingAndNonExistingMediaSourcesAdded(self):
        mediaSource1 = MediaSource(os.path.join(self.tempDirPath, "video"), MediaType.video)
        mediaSource2 = MediaSource(os.path.join(self.tempDirPath, "missing-dir"), MediaType.video)
        expected = tasks.UpdateLibrary(mediaSource1)
        self.createDir("video")

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_created") as waiter:
                sut.watch([mediaSource1, mediaSource2])
                self.createFile("video/movie.mkv")
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)


class Watcher_Dispose_TestCase(WatcherTestCaseBase, unittest.TestCase):
    def test_doesNotWatchForChanges_afterClear(self):
        mediaSource = MediaSource(self.tempDirPath, MediaType.video)

        with Watcher(self.taskManagerMock) as sut:
            sut.watch([mediaSource])
            sut.clear()
            self.createFile("movie.mkv")

        self.taskAddMock.assert_not_called()

    @patch.object(EventHandler, "on_created", side_effect=Exception())
    def test_doesNotWatchForChanges_whenExceptionOccursDuringFileSystemEventsHandling(self, *args):
        mediaSource = MediaSource(self.tempDirPath, MediaType.video)

        with Watcher(self.taskManagerMock) as sut:
            sut.watch([mediaSource])
            self.createFile("movie.mkv")  # Should fail
            self.deleteFile("movie.mkv")  # Should not be called

        self.taskAddMock.assert_not_called()

    def test_doesNotWatchForChanges_afterExitingTheWithContext(self):
        mediaSource = MediaSource(self.tempDirPath, MediaType.video)

        with Watcher(self.taskManagerMock) as sut:
            sut.watch([mediaSource])
        self.createFile("movie.mkv")

        self.taskAddMock.assert_not_called()

    def test_endsItsOwnThread_afterExitingTheWithContext(self):
        """
        The test asserts that no child threads are left running upon exiting
        with-statement context.
        """

        mediaSource = MediaSource(self.tempDirPath, MediaType.video)

        with Watcher(self.taskManagerMock) as sut:
            sut.watch([mediaSource])

        self.assertEqual(threading.active_count(), 1)

    @patch.object(EventHandler, "on_created", side_effect=Exception())
    def test_endsItsOwnThread_whenExceptionOccursDuringFileSystemEventsHandling(self, *args):
        """
        Not the best way of waiting in this test, as we are relying on "observer",
        which is an internal detail of the class, but I didn't find a better way.

        Without waiting the test is passing, while there was a bug with the observers
        not being cleaned properly in __exit__. As a result of that bug, if an exception
        occurred during file system event handing, Kodi was getting stuck on exit,
        because the add-on was still running due to alive watchers.
        """

        mediaSource = MediaSource(self.tempDirPath, MediaType.video)

        with Watcher(self.taskManagerMock) as sut:
            sut.watch([mediaSource])
            self.createFile("movie.mkv")
            while sut.observer.is_alive():
                time.sleep(0.1)

        self.assertEqual(threading.active_count(), 1)


if __name__ == "__main__":
    unittest.main()
