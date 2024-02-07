import os


def isHidden(basePath, path):
    """
    Checks whether the final component of the path itself is hidden or
    it's placed inside a parent directory that is hidden. Traverses up
    to the parent directories until basePath is reached.

    Supports only Unix style hidden files and directories, which is when
    their name starts with ".". No support for Windows hidden attribute.
    It's done for simplicity and for performance reasons as well, as only
    path name need to be checked, no need to access file system and check
    file or directory hidden attribute for Windows.

    "basePath" and "path" parameters should be absolute paths.
    """

    normPath = os.path.normpath(path)
    baseName = os.path.basename(normPath)

    if baseName.startswith("."):
        return True

    dirPath = os.path.dirname(normPath)
    normDirPath = os.path.normpath(dirPath)

    if len(normDirPath) == 0:
        return False
    if normDirPath == os.path.normpath(basePath):
        return False

    return isHidden(basePath, dirPath)


def getFileExt(path):
    return os.path.splitext(path)[1]
