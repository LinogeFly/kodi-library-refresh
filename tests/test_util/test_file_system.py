import sys
from parameterized import parameterized
import unittest
from resources.lib.util.file_system import isHidden


class IsHiddenTestCase(unittest.TestCase):
    @parameterized.expand(
        [
            ("/media/storage", "media/storage/video/.movie.mkv", True),
            ("/media/storage", "/media/storage/video/.movie.mkv", True),
            ("/media/storage", "/media/storage/video/movie.mkv", False),
            ("/media/.storage", "/media/.storage/video/movie.mkv", False),
        ]
    )
    @unittest.skipUnless(sys.platform in ["linux", "darwin"], "Unix-like OS specific tests.")
    def test_returnsExpected_forUnixStylePaths(self, basePath, path, expected: bool):
        result = isHidden(basePath, path)
        self.assertEqual(result, expected)

    @parameterized.expand(
        [
            ("D:\Media", "D:\Media\Video\.movie.mkv", True),
            ("D:\Media", "D:\Media\.Video\movie.mkv", True),
            ("D:\Media", "D:\Media\Video\movie.mkv", False),
            ("D:\.Media", "D:\.Media\Video\movie.mkv", False),
        ]
    )
    @unittest.skipUnless(sys.platform.startswith("win"), "Windows specific tests.")
    def test_returnsExpected_forWindowsPaths(self, basePath, path, expected: bool):
        result = isHidden(basePath, path)
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
