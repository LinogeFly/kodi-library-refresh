import threading
import unittest
from unittest.mock import MagicMock, PropertyMock, patch
import time
import xbmc
from resources.lib.player import Player
import resources.lib.tasks as tasks
import resources.lib.task_handling as task_handling
import resources.lib.library as library
from resources.lib.task_management import TaskManager
from resources.lib.monitoring import Monitor


"""
Some tests here utilize sleep of 0.1 seconds before asserting. That is
done in order to give a little bit of breathing room for the TaskManager
thread so it can get its tasks queued up and executed.

Some other tests here set up scenarios with certain delays, using 0.1
seconds as a step, and then assert based on those delays. Not maybe the
best way to test multi-threading behavior, but 0.1 seconds step seems
to be plenty.
"""


@patch.object(TaskManager, "DEBOUNCE_WAIT", new_callable=PropertyMock, return_value=0)
@patch.object(xbmc.Player, "isPlaying", return_value=False)
@patch.object(task_handling.UpdateLibraryTaskHandler, "execute")
@patch.object(task_handling.CleanLibraryTaskHandler, "execute")
class TaskManager_AddTasks_TestCase(unittest.TestCase):
    def test_executesCleanLibraryTask_whenTaskAdded(self, cleanMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.1)

        cleanMock.assert_called_once()

    def test_executesUpdateLibraryTask_whenTaskAdded(self, cleanMock: MagicMock, updateMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.UpdateLibrary(mediaSource))
            time.sleep(0.1)

        updateMock.assert_called_once()

    def test_queuesUpOnlyOneCleanLibraryTask_whenMultipleTasksAddedWithTheSameMediaSource(
        self, cleanMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        cleanMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))  # Starts executing immediately
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource))  # Gets queued up
            sut.add(tasks.CleanLibrary(mediaSource))  # Does not get queued up
            time.sleep(0.6)

        self.assertEqual(cleanMock.call_count, 2)

    def test_queuesUpMultipleCleanLibraryTasks_whenMultipleTasksAddedWithDifferentMediaSource(
        self, cleanMock: MagicMock, *args
    ):
        mediaSource1 = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        mediaSource2 = library.MediaSource("~/Downloads/music", library.MediaType.music)
        cleanMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource1))  # Starts executing immediately
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource1))  # Gets queued up
            sut.add(tasks.CleanLibrary(mediaSource2))  # Gets queued up as well
            time.sleep(0.6)

        self.assertEqual(cleanMock.call_count, 3)

    def test_queuesUpOnlyOneUpdateLibraryTask_whenMultipleTasksAddedWithTheSameMediaSource(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        updateMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            # Starts executing immediately
            sut.add(tasks.UpdateLibrary(mediaSource))
            time.sleep(0.1)
            # Gets queued up
            sut.add(tasks.UpdateLibrary(mediaSource))
            # Does not get queued up
            sut.add(tasks.UpdateLibrary(mediaSource))
            time.sleep(0.6)

        self.assertEqual(updateMock.call_count, 2)

    def test_queuesUpMultipleUpdateLibraryTasks_whenMultipleTasksAddedWithDifferentMediaSource(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource1 = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        mediaSource2 = library.MediaSource("~/Downloads/music", library.MediaType.music)
        updateMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.UpdateLibrary(mediaSource1))  # Starts executing immediately
            time.sleep(0.1)
            sut.add(tasks.UpdateLibrary(mediaSource1))  # Gets queued up
            sut.add(tasks.UpdateLibrary(mediaSource2))  # Gets queued up as well
            time.sleep(0.6)

        self.assertEqual(updateMock.call_count, 3)

    def test_queuesUpMultipleTasks_whenMultipleDifferentTasksAddedWithTheSameMediaSource(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        cleanMock.side_effect = lambda: time.sleep(0.2)
        updateMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))  # Starts executing immediately
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource))  # Gets queued up
            # Gets queued up as well as it has a different type
            sut.add(tasks.UpdateLibrary(mediaSource))
            time.sleep(0.6)

        self.assertEqual(cleanMock.call_count, 2)
        self.assertEqual(updateMock.call_count, 1)


@patch.object(xbmc.Player, "isPlaying", return_value=False)
@patch.object(task_handling.UpdateLibraryTaskHandler, "execute")
@patch.object(task_handling.CleanLibraryTaskHandler, "execute")
class TaskManager_DebounceTasks_TestCase(unittest.TestCase):
    def setUp(self):
        self.debouncePatcher = patch.object(TaskManager, "DEBOUNCE_WAIT", new_callable=PropertyMock)
        self.debounceMock = self.debouncePatcher.start()

    def tearDown(self):
        self.debouncePatcher.stop()

    def test_debouncesExtraTasks_whenMultipleSameTypeSameMediaSourceTasksGetAddedFast(
        self, cleanMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        self.debounceMock.return_value = 0.2

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.1)  # Wait less than debounce wait time
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.3)  # Wait more than debounce wait time

        cleanMock.assert_called_once()

    def test_debouncesExtraTasks_whenMultipleSameTypeSameMediaSourceTasksGetAddedFastPastDebounceWaitTime(
        self, cleanMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        self.debounceMock.return_value = 0.2

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            # Wait less than debounce wait time
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource))
            # Wait less than debounce wait time, but in total we should be already waiting
            # a little bit longer than debounce wait time.
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource))
            # Wait more than debounce wait time
            time.sleep(0.3)

        cleanMock.assert_called_once()

    def test_executesAllTasks_whenMultipleSameTypeSameMediaSourceTasksGetAddedSlow(self, cleanMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        self.debounceMock.return_value = 0.1

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.2)  # Wait more than debounce wait time
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.2)  # Wait more than debounce wait time

        self.assertEqual(cleanMock.call_count, 2)

    def test_executesAllTasks_whenMultipleSameTypeDifferentMediaSourceTasksGetAddedFast(
        self, cleanMock: MagicMock, *args
    ):
        mediaSource1 = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        mediaSource2 = library.MediaSource("~/Downloads/music", library.MediaType.music)
        self.debounceMock.return_value = 0.1

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource1))
            time.sleep(0.1)  # Wait less than debounce wait time
            sut.add(tasks.CleanLibrary(mediaSource2))
            time.sleep(0.3)  # Wait more than debounce wait time

        self.assertEqual(cleanMock.call_count, 2)

    def test_executesAllTasks_whenMultipleSameTypeDifferentMediaSourceTasksGetAddedSlow(
        self, cleanMock: MagicMock, *args
    ):
        mediaSource1 = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        mediaSource2 = library.MediaSource("~/Downloads/music", library.MediaType.music)
        self.debounceMock.return_value = 0.1

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource1))
            time.sleep(0.2)  # Wait more than debounce wait time
            sut.add(tasks.CleanLibrary(mediaSource2))
            time.sleep(0.2)  # Wait more than debounce wait time

        self.assertEqual(cleanMock.call_count, 2)

    def test_executesAllTasks_whenMultipleDifferentTypeSameMediaSourceTasksGetAddedFast(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        self.debounceMock.return_value = 0.2

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.1)  # Wait less than debounce wait time
            sut.add(tasks.UpdateLibrary(mediaSource))
            time.sleep(0.3)  # Wait more than debounce wait time

        cleanMock.assert_called_once()
        updateMock.assert_called_once()

    def test_executesAllTasks_whenMultipleDifferentTypeSameMediaSourceTasksGetAddedSlow(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        self.debounceMock.return_value = 0.1

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.2)  # Wait more than debounce wait time
            sut.add(tasks.UpdateLibrary(mediaSource))
            time.sleep(0.2)  # Wait more than debounce wait time

        cleanMock.assert_called_once()
        updateMock.assert_called_once()

    def test_executesAllTasks_whenMultipleDifferentTypeDifferentMediaSourceTasksGetAddedFast(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource1 = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        mediaSource2 = library.MediaSource("~/Downloads/music", library.MediaType.music)
        self.debounceMock.return_value = 0.1

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource1))
            time.sleep(0.1)  # Wait less than debounce wait time
            sut.add(tasks.UpdateLibrary(mediaSource2))
            time.sleep(0.3)  # Wait more than debounce wait time

        cleanMock.assert_called_once()
        updateMock.assert_called_once()

    def test_executesAllTasks_whenMultipleDifferentTypeDifferentMediaSourceTasksGetAddedSlow(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource1 = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        mediaSource2 = library.MediaSource("~/Downloads/music", library.MediaType.music)
        self.debounceMock.return_value = 0.1

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource1))
            time.sleep(0.2)  # Wait more than debounce wait time
            sut.add(tasks.UpdateLibrary(mediaSource2))
            time.sleep(0.2)  # Wait more than debounce wait time

        cleanMock.assert_called_once()
        updateMock.assert_called_once()


@patch.object(TaskManager, "DEBOUNCE_WAIT", new_callable=PropertyMock, return_value=0)
@patch.object(xbmc.Player, "isPlaying", return_value=True)
@patch.object(task_handling.CleanLibraryTaskHandler, "execute")
class TaskManager_TasksDuringPlayback_TestCase(unittest.TestCase):
    def test_doestNotExecuteQueuedUpTask_duringPlayback(self, executeMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.1)

        executeMock.assert_not_called()

    def test_executeQueuedUpTask_afterPlaybackStops(self, executeMock: MagicMock, isPlayingMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        player = Player()

        # Inject own instance of Player, so we can call playback related methods
        # from outside of TaskManager, somewhat simulating what xbmc.Player does.
        with patch.object(xbmc.Player, "__new__", return_value=player):
            with TaskManager(Monitor()) as sut:
                # Should queue up the task because something is playing
                isPlayingMock.return_value = True
                sut.add(tasks.CleanLibrary(mediaSource))
                time.sleep(0.1)

                # Should pick up queued up task and execute it
                isPlayingMock.return_value = False
                player.onPlayBackStopped()
                time.sleep(0.1)

        executeMock.assert_called_once()

    def test_executeQueuedUpTask_afterPlaybackEnds(self, executeMock: MagicMock, isPlayingMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        player = Player()

        # Inject own instance of Player, so we can call playback related methods
        # from outside of TaskManager, somewhat simulating what xbmc.Player does.
        with patch.object(xbmc.Player, "__new__", return_value=player):
            with TaskManager(Monitor()) as sut:
                # Should queue up the task because something is playing
                isPlayingMock.return_value = True
                sut.add(tasks.CleanLibrary(mediaSource))
                time.sleep(0.1)

                # Should pick up queued up task and execute it
                isPlayingMock.return_value = False
                player.onPlayBackEnded()
                time.sleep(0.1)

        executeMock.assert_called_once()


@patch.object(TaskManager, "DEBOUNCE_WAIT", new_callable=PropertyMock, return_value=0)
@patch.object(xbmc.Player, "isPlaying", return_value=False)
@patch.object(task_handling.UpdateLibraryTaskHandler, "execute")
@patch.object(task_handling.CleanLibraryTaskHandler, "execute")
class TaskManager_Dispose_TestCase(unittest.TestCase):
    def test_doesNotExecuteQueuedUpTasks_afterClear(self, cleanMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        cleanMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))  # Starts executing immediately
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource))  # Gets queued up
            # Previous task should be cleaned away from the queue
            sut.clear()
            time.sleep(0.4)

        cleanMock.assert_called_once()

    def test_doesNotExecuteQueuedUpTasks_afterExitingTheWithContext(self, cleanMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        cleanMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            # Starts executing immediately
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.1)
            # Gets queued up, but should not execute upon exiting the "with" context
            sut.add(tasks.CleanLibrary(mediaSource))
        time.sleep(0.4)

        cleanMock.assert_called_once()

    def test_doesNotExecuteNewTasks_afterExitingTheWithContext(self, cleanMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)

        with TaskManager(Monitor()) as sut:
            pass
        sut.add(tasks.CleanLibrary(mediaSource))
        time.sleep(0.1)

        cleanMock.assert_not_called()

    def test_stopsWaitingForNewTasks_whenExceptionOccursDuringTaskExecution(
        self, cleanMock: MagicMock, updateMock: MagicMock, *args
    ):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        updateMock.side_effect = Exception()
        cleanMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.UpdateLibrary(mediaSource))  # Should fail
            time.sleep(0.1)
            sut.add(tasks.CleanLibrary(mediaSource))  # Should not get queued up
            time.sleep(0.3)

        cleanMock.assert_not_called()

    def test_endsItsOwnThread_afterExitingTheWithContext(self, *args):
        """
        The test asserts that no child threads are left running upon exiting
        with-statement context. Which is pretty much is about making sure that
        "join" method is called for the thread in the __exit__ function.
        """

        with TaskManager(Monitor()):
            time.sleep(0.1)

        self.assertEqual(threading.active_count(), 1)

    def test_endsItsOwnThread_afterExitingTheWithContextDuringTaskExecution(self, cleanMock: MagicMock, *args):
        mediaSource = library.MediaSource("~/Downloads/movies", library.MediaType.video)
        cleanMock.side_effect = lambda: time.sleep(0.2)

        with TaskManager(Monitor()) as sut:
            sut.add(tasks.CleanLibrary(mediaSource))
            time.sleep(0.1)

        self.assertEqual(threading.active_count(), 1)

    def test_endsItsOwnThread_afterExitingTheWithContextDuringPlayback(self, isPlaying: MagicMock, *args):
        isPlaying.return_value = True

        with TaskManager(Monitor()):
            time.sleep(0.1)

        self.assertEqual(threading.active_count(), 1)


if __name__ == "__main__":
    unittest.main()
