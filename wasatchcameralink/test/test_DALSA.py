""" tests for a wasatch photonics cobra over dalsa card.
"""

import unittest
import logging

from wasatchcameralink.DALSA import Cobra
from wasatchcameralink.DALSA import BaslerSprint4K

logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger()

class TestCobra(unittest.TestCase):

    def setUp(self):
        self.dev = Cobra()

    def test_pipe_cycle(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 2048)

        self.assertTrue(self.dev.close_pipe())

class TestBasler4K(unittest.TestCase):

    def setUp(self):
        self.dev = BaslerSprint4K()

    def test_pipe_cycle(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 4096)

        self.assertTrue(self.dev.close_pipe())

if __name__ == "__main__":
    unittest.main()

