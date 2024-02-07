from unittest.mock import patch
import threading


class Waiter:
    """
    A support class for tests. Helps with waiting for function calls
    to be executed once or X amount times.

    What the class does is it patches an object's function with a wrapper
    function. The wrapper calls the original function and then
    waits increments the call counter by 1. Then the "wait" method can be
    used in order to wait for the original function to be called X amount
    of times (1 by default).

    If the function doesn't get called at all, the "wait" method will time
    out after TIMEOUT seconds.
    """

    TIMEOUT = 5

    def __init__(self, target, attribute) -> None:
        self.orig = getattr(target, attribute)
        self.target = target
        self.attribute = attribute
        self.calledTimes = 0
        self.calledLock = threading.Condition()

    def __enter__(self):
        def wrapper(mock, *args):
            with self.calledLock:
                self.orig(mock, *args)
                self.calledTimes += 1
                self.calledLock.notify()

        self.patcher = patch.object(self.target, self.attribute, new=wrapper)
        self.patcher.start()

        return self

    def __exit__(self, *args):
        self.patcher.stop()

    def wait(self, *, times=1):
        with self.calledLock:
            while self.calledTimes < times:
                called = self.calledLock.wait(self.TIMEOUT)
                if not called:
                    return
