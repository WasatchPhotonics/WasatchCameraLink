""" tests for a wasatch photonics cobra over dalsa card.
"""

import time
import numpy
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

    def test_gain(self):
        # Make sure no light is reaching the detector
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        avg_default = numpy.average(data)

        time.sleep(0.5)
        result = self.dev.set_gain(100)
        result, data = self.dev.grab_pipe()
        avg_low_gain = numpy.average(data)

        log.info("uh %s, %s" % ( avg_default, avg_low_gain))

        gain_diff_threshold = 1000
        gain_diff = abs(avg_low_gain - avg_default)
        self.assertGreater(gain_diff, gain_diff_threshold)

        # Now set it back to default 187, and make sure the difference
        # is minimal
        result = self.dev.set_gain(187)
        result, data = self.dev.grab_pipe()
        new_default = numpy.average(data)


        new_diff = abs(new_default - avg_default)
        self.assertLess(new_diff, 10)
        self.assertTrue(self.dev.close_pipe())

    def test_new_gain(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 2048)

        self.assertTrue(self.dev.open_write_close("gain 187"))
        self.assertTrue(self.dev.close_pipe())

        self.assertTrue(result)

        

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

