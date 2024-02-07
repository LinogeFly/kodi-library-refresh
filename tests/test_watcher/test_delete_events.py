import sys
import unittest
import resources.lib.tasks as tasks
from resources.lib.library import MediaSource, MediaType
from resources.lib.watcher import EventHandler, Watcher
from parameterized import parameterized
from tests.support import Waiter
from tests.test_watcher.support import WatcherTestCaseBase


@unittest.skipIf(sys.platform.startswith("win"), "Unix-like OS specific tests.")
class Watcher_DeleteEventOnReasonableOperatingSystems_TestCase(WatcherTestCaseBase, unittest.TestCase):
    @parameterized.expand(
        [
            (MediaType.video, "movie.mkv"),
            (MediaType.music, "song.mp3"),
        ]
    )
    def test_addsCleanTask_whenFileIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, ".movie.mkv"),
            (MediaType.video, "RARBG.txt"),
            (MediaType.video, "no-ext"),
            (MediaType.music, ".song.mkv"),
            (MediaType.music, "RARBG.txt"),
            (MediaType.music, "no-ext"),
        ]
    )
    def test_doesNotAddAnyTasks_whenFileIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    @parameterized.expand(
        [
            (MediaType.video, "video"),
            (MediaType.video, ".video"),
            (MediaType.music, "music"),
            (MediaType.music, ".music"),
        ]
    )
    def test_doesNotAddAnyTasks_whenDirectoryIsDeleted(self, mediaType, dirPath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createDir(dirPath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteDir(dirPath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    @parameterized.expand(
        [
            (MediaType.video, "video/movie.mkv"),
            (MediaType.music, "music/song.mp3"),
        ]
    )
    def test_addsCleanTask_whenFileInDirectoryIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, "video/.movie.mkv"),
            (MediaType.video, "video/RARBG.txt"),
            (MediaType.video, "video/no-ext"),
            (MediaType.video, ".video/movie.mkv"),
            (MediaType.video, ".video/.movie.mkv"),
            (MediaType.video, ".video/RARBG.txt"),
            (MediaType.video, ".video/no-ext"),
            (MediaType.music, "music/.song.mp3"),
            (MediaType.music, "music/RARBG.txt"),
            (MediaType.music, "music/no-ext"),
            (MediaType.music, ".music/song.mp3"),
            (MediaType.music, ".music/.song.mp3"),
            (MediaType.music, ".music/RARBG.txt"),
            (MediaType.music, ".music/no-ext"),
        ]
    )
    def test_doesNotAddAnyTasks_whenFileInDirectoryIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_not_called()


@unittest.skipUnless(sys.platform.startswith("win"), "Windows specific tests.")
class Watcher_DeleteEventOnWindows_TestCase(WatcherTestCaseBase, unittest.TestCase):
    """
    Delete event has different handling rules. The reasons for that are:

    1. Looks like in Watchdog delete event handler we can't know if it was a file
       or a directory deleted. To my understanding that's because ReadDirectoryChangesW
       Windows API doesn't provide that information. We also can't check that ourselves,
       because a file/directory has already been deleted by the time we receive a file
       system event.

       The way we check if it was a directory of a file deleted is basically by checking
       the deleted item's extension. Not pretty, but oh well.
    2. When directory with files is deleted in Windows we only get a delete event for the
       directory, but no events for the deleted files in that directory. As a result,
       we have to always create a library cleaning task when directory is deleted, despite
       it possibly being empty, or contain non supported media files.
    """

    @parameterized.expand(
        [
            (MediaType.video, "movie.mkv"),
            (MediaType.video, "no-ext"),
            (MediaType.music, "song.mp3"),
            (MediaType.music, "no-ext"),
        ]
    )
    def test_addsCleanTask_whenFileIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, ".movie.mkv"),
            (MediaType.video, "RARBG.txt"),
            (MediaType.music, ".song.mkv"),
            (MediaType.music, "RARBG.txt"),
        ]
    )
    def test_doesNotAddAnyTasks_whenFileIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    @parameterized.expand(
        [
            (MediaType.video, "video"),
            (MediaType.music, "music"),
        ]
    )
    def test_addsCleanTask_whenDirectoryIsDeleted(self, mediaType, dirPath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createDir(dirPath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteDir(dirPath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, ".video"),
            (MediaType.music, ".music"),
        ]
    )
    def test_doesNotAddAnyTasks_whenDirectoryIsDeleted(self, mediaType, dirPath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createDir(dirPath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteDir(dirPath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    @parameterized.expand(
        [
            (MediaType.video, "video/movie.mkv"),
            (MediaType.video, "video/no-ext"),
            (MediaType.music, "music/song.mp3"),
            (MediaType.music, "music/no-ext"),
        ]
    )
    def test_addsCleanTask_whenFileInDirectoryIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, "video/.movie.mkv"),
            (MediaType.video, "video/RARBG.txt"),
            (MediaType.video, ".video/movie.mkv"),
            (MediaType.video, ".video/.movie.mkv"),
            (MediaType.video, ".video/RARBG.txt"),
            (MediaType.video, ".video/no-ext"),
            (MediaType.music, "music/.song.mp3"),
            (MediaType.music, "music/RARBG.txt"),
            (MediaType.music, ".music/song.mp3"),
            (MediaType.music, ".music/.song.mp3"),
            (MediaType.music, ".music/RARBG.txt"),
            (MediaType.music, ".music/no-ext"),
        ]
    )
    def test_doesNotAddAnyTasks_whenFileInDirectoryIsDeleted(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_deleted") as waiter:
                sut.watch([mediaSource])
                self.deleteFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
