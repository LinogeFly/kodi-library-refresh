import unittest
import resources.lib.tasks as tasks
from resources.lib.library import MediaSource, MediaType
from resources.lib.watcher import EventHandler, Watcher
from parameterized import parameterized
from tests.support import Waiter
from tests.test_watcher.support import WatcherTestCaseBase


class WatcherTestCase(WatcherTestCaseBase, unittest.TestCase):
    @parameterized.expand(
        [
            (MediaType.video, "movie.mkv"),
            (MediaType.music, "song.mp3"),
        ]
    )
    def test_addsUpdateTask_whenFileIsCreated(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.UpdateLibrary(mediaSource)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_created") as waiter:
                sut.watch([mediaSource])
                self.createFile(filePath)
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
    def test_doesNotAddAnyTasks_whenFileIsCreated(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_created") as waiter:
                sut.watch([mediaSource])
                self.createFile(filePath)
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
    def test_doesNotAddAnyTasks_whenDirectoryIsCreated(self, mediaType, dirPath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_created") as waiter:
                sut.watch([mediaSource])
                self.createDir(dirPath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    @parameterized.expand(
        [
            (MediaType.video, "video/movie.mkv"),
            (MediaType.music, "music/song.mp3"),
        ]
    )
    def test_addsUpdateTask_whenFileInDirectoryIsCreated(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.UpdateLibrary(mediaSource)
        self.createFileDir(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_created") as waiter:
                sut.watch([mediaSource])
                self.createFile(filePath)
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
    def test_doesNotAddAnyTasks_whenFileInDirectoryIsCreated(self, mediaType, filePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createFileDir(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_created") as waiter:
                sut.watch([mediaSource])
                self.createFile(filePath)
                waiter.wait()

        self.taskAddMock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
