import os
import tempfile
import xbmc
from resources.lib.task_management import TaskManager
from unittest.mock import Mock, patch


class WatcherTestCaseBase:
    """
    Base class for Watcher tests, which includes the following:

    - setUp and tearDown methods that create and clean temporary
      directory to for each test. The directory then mainly used
      as a media source directory to watch for the changes.
    - Helper methods to create, rename and delete files and
      directories in the temporary directory.
    - Mocks and stubs needed for the Watcher tests.

    """

    def setUp(self):
        self.taskAddMock = Mock()
        self.taskManagerMock = Mock(TaskManager)
        self.taskManagerMock.add = self.taskAddMock

        self.supportedMediaPatcher = patch.object(xbmc, "getSupportedMedia")
        self.supportedMediaMock = self.supportedMediaPatcher.start()
        self.supportedMediaMock.side_effect = self._getSupportedMediaStub

        self.tempDir = tempfile.TemporaryDirectory()
        self.tempDirPath = self.tempDir.name

    def tearDown(self):
        self.tempDir.cleanup()
        self.supportedMediaPatcher.stop()

    def createFileDir(self, filePath: str):
        """
        Creates a directory for the filepath parameter. For example,
        for "video/movie.mkv" filepath "video" directory will be
        created if it doesn't exist yet.
        """

        dirPath = os.path.dirname(os.path.normpath(filePath))
        fullDirPath = os.path.join(self.tempDirPath, dirPath)

        if len(dirPath) > 0 and not os.path.exists(fullDirPath):
            os.mkdir(fullDirPath)

    def createFile(self, filePath: str):
        fullFilePath = os.path.join(self.tempDirPath, os.path.normpath(filePath))
        self.createFileDir(filePath)  # Create the directory
        with open(fullFilePath, "wb"):  # Create the file
            pass

    def createDir(self, dirPath: str):
        fullDirPath = os.path.join(self.tempDirPath, dirPath)
        os.mkdir(fullDirPath)

    def deleteFile(self, filePath: str):
        fullFilePath = os.path.join(self.tempDirPath, os.path.normpath(filePath))
        os.remove(fullFilePath)

    def deleteDir(self, dirPath: str):
        fullDirPath = os.path.join(self.tempDirPath, os.path.normpath(dirPath))
        os.rmdir(fullDirPath)

    def renamePath(self, path: str, newPath: str):
        fullPath = os.path.join(self.tempDirPath, os.path.normpath(path))
        fullNewPath = os.path.join(self.tempDirPath, os.path.normpath(newPath))
        os.rename(fullPath, fullNewPath)

    def renameFileDir(self, filePath: str, newFilePath: str):
        """
        Renames directory for filepath parameter to the one specified
        in newFilePath parameter. For example, for parameters like this:
        video/movie.mkv -> movies/movie.mkv
        "video" directory will get renamed to "movies".
        """

        dirPath = os.path.dirname(os.path.normpath(filePath))
        newDirPath = os.path.dirname(os.path.normpath(newFilePath))
        fullDirPath = os.path.join(self.tempDirPath, dirPath)
        fullNewDirPath = os.path.join(self.tempDirPath, newDirPath)

        if fullDirPath != fullNewDirPath:
            os.rename(fullDirPath, fullNewDirPath)

    def _getSupportedMediaStub(self, mediaType: str):
        if mediaType == "video":
            return ".mkv|.mp4|"
        if mediaType == "music":
            return ".ogg|.mp3||"
        raise Exception("Invalid media type.")
