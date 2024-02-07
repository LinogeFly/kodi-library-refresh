import unittest
import xbmc
from unittest.mock import MagicMock, patch
from resources.lib.library import MediaType, Library


class Library_GetMediaSources_TestCase(unittest.TestCase):
    def setUp(self):
        self.rpcPatcher = patch.object(xbmc, "executeJSONRPC")
        self.rpcMock = self.rpcPatcher.start()
        self.rpcMock.return_value = "{}"

        self.settingsMock = MagicMock()
        self.settingsMock.return_value.isRefreshVideoEnabled.return_value = False
        self.settingsMock.return_value.isRefreshMusicEnabled.return_value = False

    def tearDown(self):
        self.rpcPatcher.stop()

    def test_callsRpcApi_whenWatchVideoSettingIsEnabled(self):
        self.settingsMock.return_value.isRefreshVideoEnabled.return_value = True
        library = Library(self.settingsMock())

        _ = library.getMediaSources()

        self.rpcMock.assert_called_once_with(
            '{"jsonrpc": "2.0", "method": "Files.GetSources", "params": { "media": "video" }, "id": 1}'
        )

    def test_doesNotCallRpcApi_whenWatchVideoSettingIsDisabled(self):
        self.settingsMock.return_value.isRefreshVideoEnabled.return_value = False
        library = Library(self.settingsMock())

        _ = library.getMediaSources()

        self.rpcMock.assert_not_called()

    def test_callsRpcApi_whenWatchMusicSettingIsEnabled(self):
        self.settingsMock.return_value.isRefreshMusicEnabled.return_value = True
        library = Library(self.settingsMock())

        _ = library.getMediaSources()

        self.rpcMock.assert_called_once_with(
            '{"jsonrpc": "2.0", "method": "Files.GetSources", "params": { "media": "music" }, "id": 1}'
        )

    def test_doesNotCallRpcApi_whenWatchMusicSettingIsDisabled(self):
        self.settingsMock.return_value.isRefreshMusicEnabled.return_value = False
        library = Library(self.settingsMock())

        _ = library.getMediaSources()

        self.rpcMock.assert_not_called()

    def test_returnsVideoSources_whenWatchVideoSettingIsEnabled(self):
        self.rpcMock.return_value = """
          {
            "id": 1,
            "jsonrpc": "2.0",
            "result": {
              "sources": [
                {
                  "file": "/media/movies",
                  "label": "Movies"
                }
              ]
            }
          }
        """
        self.settingsMock.return_value.isRefreshVideoEnabled.return_value = True
        library = Library(self.settingsMock())

        result = library.getMediaSources()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].path, "/media/movies")
        self.assertEqual(result[0].type, MediaType.video)

    def test_doesNotReturnVideoSources_whenWatchVideoSettingIsDisabled(self):
        self.rpcMock.return_value = """
          {
            "id": 1,
            "jsonrpc": "2.0",
            "result": {
              "sources": [
                {
                  "file": "/media/movies",
                  "label": "Movies"
                }
              ]
            }
          }
        """
        self.settingsMock.return_value.isRefreshVideoEnabled.return_value = False
        library = Library(self.settingsMock())

        result = library.getMediaSources()

        self.assertEqual(len(result), 0)

    def test_returnsMusicSources_whenWatchMusicSettingIsEnabled(self):
        self.rpcMock.return_value = """
          {
            "id": 1,
            "jsonrpc": "2.0",
            "result": {
              "sources": [
                {
                  "file": "/media/music",
                  "label": "Music"
                }
              ]
            }
          }
        """
        self.settingsMock.return_value.isRefreshMusicEnabled.return_value = True
        library = Library(self.settingsMock())

        result = library.getMediaSources()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].path, "/media/music")
        self.assertEqual(result[0].type, MediaType.music)

    def test_doesNotReturnMusicSources_whenWatchMusicSettingIsDisabled(self):
        self.rpcMock.return_value = """
          {
            "id": 1,
            "jsonrpc": "2.0",
            "result": {
              "sources": [
                {
                  "file": "/media/music",
                  "label": "Music"
                }
              ]
            }
          }
        """
        self.settingsMock.return_value.isRefreshMusicEnabled.return_value = False
        library = Library(self.settingsMock())

        result = library.getMediaSources()

        self.assertEqual(len(result), 0)

    def test_returnsMultipleVideoSources_forMultipathKodiVideoSources(self):
        self.rpcMock.return_value = """
		{
		  "id": 1,
		  "jsonrpc": "2.0",
		  "result": {
			"limits": { "end": 2, "start": 0, "total": 2 },
			"sources": [
			  {
				"file": "multipath://%2fmedia%2fmovies/%2fmedia%2ftv-series/",
				"label": "Video"
			  }
			]
		  }
		}
        """
        self.settingsMock.return_value.isRefreshVideoEnabled.return_value = True
        library = Library(self.settingsMock())

        result = library.getMediaSources()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].path, "/media/movies")
        self.assertEqual(result[0].type, MediaType.video)
        self.assertEqual(result[1].path, "/media/tv-series")
        self.assertEqual(result[1].type, MediaType.video)

    def test_returnsMultipleMusicSources_forMultipathKodiMusicSources(self):
        self.rpcMock.return_value = """
		{
		  "id": 1,
		  "jsonrpc": "2.0",
		  "result": {
			"limits": { "end": 2, "start": 0, "total": 2 },
			"sources": [
			  {
				"file": "multipath://%2fmedia%2fmusic%2f80s/%2fmedia%2fmusic%2f90s/",
				"label": "Music"
			  }
			]
		  }
		}
        """
        self.settingsMock.return_value.isRefreshMusicEnabled.return_value = True
        library = Library(self.settingsMock())

        result = library.getMediaSources()

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0].path, "/media/music/80s")
        self.assertEqual(result[0].type, MediaType.music)
        self.assertEqual(result[1].path, "/media/music/90s")
        self.assertEqual(result[1].type, MediaType.music)


if __name__ == "__main__":
    unittest.main()
