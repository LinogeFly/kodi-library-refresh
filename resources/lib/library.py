from enum import Enum
import json
import xbmc
from typing import List, NamedTuple
from urllib.parse import unquote
from resources.lib.settings import Settings
import resources.lib.logging as logging


class MediaType(Enum):
    video = 1
    music = 2


class MediaSource(NamedTuple):
    path: str
    type: MediaType


class InvalidMediaTypeException(Exception):
    def __init__(self, mediaType: MediaType) -> None:
        message = 'Not supported media type "%s".' % mediaType.name
        super().__init__(message)


class Library:
    def __init__(self, settings: Settings):
        self.logger = logging.getLogger(self)
        self.settings = settings

    def getMediaSources(self) -> List[MediaSource]:
        videoPaths = self._getMediaSourcePathsFor("video") if self.settings.isRefreshVideoEnabled() else []
        musicPaths = self._getMediaSourcePathsFor("music") if self.settings.isRefreshMusicEnabled() else []

        return [MediaSource(p, MediaType.video) for p in videoPaths] + [
            MediaSource(p, MediaType.music) for p in musicPaths
        ]

    def _getMediaSourcePathsFor(self, type: str):
        query = (
            b'{"jsonrpc": "2.0", "method": "Files.GetSources", "params": { "media": "%b" }, "id": 1}' % type.encode()
        )
        response = json.loads(xbmc.executeJSONRPC(query.decode()))
        self.logger.debug('Fetched "%s" sources using JSONRPC API. Response: "%s".' % (type, response))

        sourcePaths = [s["file"] for s in response.get("result", {}).get("sources", [])]
        paths = self._splitMultipaths(sourcePaths)

        return paths

    def _splitMultipaths(self, paths):
        result = []
        for path in paths:
            if path.startswith("multipath://"):
                subpaths = path.split("multipath://")[1].split("/")
                subpaths = [unquote(path) for path in subpaths if path != ""]
                result.extend(subpaths)
            else:
                result.append(path)

        return result
