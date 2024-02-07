import xbmc
import xbmcgui
import xbmcaddon

_addonName = xbmcaddon.Addon().getAddonInfo("name")
_addonId = xbmcaddon.Addon().getAddonInfo("id")


class Logger:
    def __init__(self, category):
        self.category = category

    def debug(self, message):
        xbmc.log("%s/%s: %s" % (_addonId, self.category, message), xbmc.LOGDEBUG)

    def info(self, message):
        xbmc.log("%s/%s: %s" % (_addonId, self.category, message), xbmc.LOGINFO)

    def warn(self, message):
        xbmc.log("%s/%s: %s" % (_addonId, self.category, message), xbmc.LOGWARNING)

    def error(self, message):
        xbmc.log("%s/%s: %s" % (_addonId, self.category, message), xbmc.LOGERROR)


def getLogger(obj):
    if type(obj) is str:
        return Logger(obj)

    fullName = _getFullyQualifiedTypeName(obj)
    return Logger(fullName)


def notifyError(message="Check the log for more information."):
    xbmcgui.Dialog().notification(
        f"{_addonName} error",
        message,
        xbmcgui.NOTIFICATION_ERROR,
    )


def notifyWarning(message):
    xbmcgui.Dialog().notification(
        f"{_addonName} warning",
        message,
        xbmcgui.NOTIFICATION_WARNING,
    )


def notifyOnError(f):
    """
    Decorator that shows a notification message in UI if exception occurs
    in a function call. Main use for this one is to decorate overridden
    methods in classes from Kodi modules, for example xbmc.Monitor.

    Looks like errors inside overridden methods in classes from Kodi
    modules don't raise up neither in the main thread nor in the child
    threads. As a result, uncaught errors go completely unnoticed.
    That's why we catch and notify about those with the decorator.
    """

    def _try(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            notifyError()
            raise

    return _try


def _getFullyQualifiedTypeName(obj):
    cls = obj.__class__
    module = cls.__module__

    # to avoid outputs like 'builtins.str'
    if module == "builtins":
        return cls.__qualname__

    return module + "." + cls.__qualname__
