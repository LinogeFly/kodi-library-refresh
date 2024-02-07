from resources.lib.library import MediaSource


class UpdateLibrary:
    def __init__(self, mediaSource: MediaSource):
        self.mediaSource = mediaSource

    def __str__(self) -> str:
        return 'Library update for "%s" media type' % self.mediaSource.type.name

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other) and self.mediaSource.type == other.mediaSource.type


class CleanLibrary:
    def __init__(self, mediaSource: MediaSource):
        self.mediaSource = mediaSource

    def __str__(self) -> str:
        return 'Library clean for "%s" media type' % self.mediaSource.type.name

    def __eq__(self, other: object) -> bool:
        return type(self) == type(other) and self.mediaSource.type == other.mediaSource.type
