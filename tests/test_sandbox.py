import unittest
from unittest.mock import patch

class Sandbox_TestCase(unittest.TestCase):
    def test_readyPlayerOne(self):
        playerBase = PlayerBase()
        # with patch("test_sandbox.Player", autospec=True) as mock:
        #     player = Player()
        #     mock.onPlayBackStopped()



class PlayerBase():
    def onPlayBackStopped(self):
        pass

class Player(PlayerBase):
    def __init__(self):
        super().__init__()

    def onPlayBackStopped(self):
        print("--- Player.onPlayBackStopped")

class PlayerStub(Player):
    def __init__(self):
        super().__init__()