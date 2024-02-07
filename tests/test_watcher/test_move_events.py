import unittest
from unittest.mock import call
import resources.lib.tasks as tasks
from resources.lib.library import MediaSource, MediaType
from resources.lib.watcher import EventHandler, Watcher
from parameterized import parameterized
from tests.support import Waiter
from tests.test_watcher.support import WatcherTestCaseBase


class WatcherTestCase(WatcherTestCaseBase, unittest.TestCase):
    ## File scenarios

    @parameterized.expand(
        [
            (MediaType.video, "movie.mkv", "scary-movie.mkv"),
            (MediaType.music, "song.mp3", "catchy-song.mp3"),
        ]
    )
    def test_addsUpdateAndCleanTask_whenFileIsRenamed(self, mediaType, filePath, newFilePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected1 = tasks.UpdateLibrary(mediaSource)
        expected2 = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renamePath(filePath, newFilePath)
                waiter.wait()

        self.assertEqual(self.taskAddMock.call_count, 2)
        self.assertEqual(
            self.taskAddMock.call_args_list,
            [
                call(
                    expected1,
                ),
                call(
                    expected2,
                ),
            ],
        )

    @parameterized.expand(
        [
            (MediaType.video, ".movie.mkv", "movie.mkv"),
            (MediaType.music, ".song.mp3", "song.mp3"),
        ]
    )
    def test_addsUpdateTask_whenFileIsRenamed(self, mediaType, filePath, newFilePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.UpdateLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renamePath(filePath, newFilePath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, "movie.mkv", ".movie.mkv"),
            (MediaType.music, "song.mp3", ".song.mp3"),
        ]
    )
    def test_addsCleanTask_whenFileIsRenamed(self, mediaType, filePath, newFilePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renamePath(filePath, newFilePath)
                waiter.wait()

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, ".movie.mkv", ".dirty-movie.mkv"),
            (MediaType.video, "RARBG.txt", "README.txt"),
            (MediaType.video, "RARBG.txt", ".RARBG.txt"),
            (MediaType.video, ".RARBG.txt", "RARBG.txt"),
            (MediaType.video, "no-ext", "no-extension"),
            (MediaType.video, "no-ext", ".no-ext"),
            (MediaType.video, ".no-ext", "no-ext"),
            (MediaType.video, ".video/movie.mkv", ".video/scary-movie.mkv"),
            (MediaType.music, ".song.mp3", ".nasty-song.mp3"),
            (MediaType.music, "RARBG.txt", "README.txt"),
            (MediaType.music, "RARBG.txt", ".RARBG.txt"),
            (MediaType.music, ".RARBG.txt", "RARBG.txt"),
            (MediaType.music, "no-ext", "no-extension"),
            (MediaType.music, "no-ext", ".no-ext"),
            (MediaType.music, ".no-ext", "no-ext"),
            (MediaType.music, ".music/song.mp3", ".music/catchy-song.mp3"),
        ]
    )
    def test_doesNotAddAnyTasks_whenFileIsRenamed(self, mediaType, filePath, newFilePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renamePath(filePath, newFilePath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    ## Directory (empty) scenarios

    @parameterized.expand(
        [
            (MediaType.video, "video", "movies"),
            (MediaType.video, "video", ".video"),
            (MediaType.video, ".video", "video"),
            (MediaType.music, "music", "songs"),
            (MediaType.music, "music", ".music"),
            (MediaType.music, ".music", "music"),
        ]
    )
    def test_doesNotAddAnyTasks_whenEmptyDirectoryIsRenamed(self, mediaType, dirPath, newDirPath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        self.createDir(dirPath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renamePath(dirPath, newDirPath)
                waiter.wait()

        self.taskAddMock.assert_not_called()

    ## Directory (with files) scenarios

    @parameterized.expand(
        [
            (MediaType.video, ".video/movie.mkv", "video/movie.mkv"),
            (MediaType.music, ".music/song.mp3", "music/song.mp3"),
        ]
    )
    def test_addsUpdateTask_whenDirectoryWithFileIsRenamed(self, mediaType, filePath, newFilePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.UpdateLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renameFileDir(filePath, newFilePath)
                waiter.wait(times=2)

        self.taskAddMock.assert_called_once_with(expected)

    @parameterized.expand(
        [
            (MediaType.video, "video/movie.mkv", ".video/movie.mkv"),
            (MediaType.music, "music/song.mp3", ".music/song.mp3"),
        ]
    )
    def test_addsCleanTask_whenDirectoryWithFileIsRenamed(self, mediaType, filePath, newFilePath):
        mediaSource = MediaSource(self.tempDirPath, mediaType)
        expected = tasks.CleanLibrary(mediaSource)
        self.createFile(filePath)

        with Watcher(self.taskManagerMock) as sut:
            with Waiter(EventHandler, "on_moved") as waiter:
                sut.watch([mediaSource])
                self.renameFileDir(filePath, newFilePath)
                waiter.wait(times=2)

        self.taskAddMock.assert_called_once_with(expected)


if __name__ == "__main__":
    unittest.main()
