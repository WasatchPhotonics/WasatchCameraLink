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

    def test_speed(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        forc_res = self.dev.open_port()
        forc_res = self.dev.start_scan()
        avg_default = numpy.average(data)

        time_start = time.time()
        for i in range(255):
            result = self.dev.set_gain(100)
            result, data = self.dev.grab_pipe()
        time_stop = time.time()

        time_diff = time_stop - time_start
        log.info("time diff: %s" % time_diff)

        self.assertTrue(self.dev.close_pipe())


    def test_gain(self):
        # Make sure no light is reaching the detector when running this test

        # Yes, this is the correct order - see the barbecue application for
        # details. An alternative if speed is not required is the open write
        # close pattern in the test below
        self.assertTrue(self.dev.setup_pipe())
        result, data = self.dev.grab_pipe()
        forc_res = self.dev.open_port()
        forc_res = self.dev.start_scan()

        # Set to default gain
        result = self.dev.set_gain(187)
        result, data = self.dev.grab_pipe()
        
        avg_default = numpy.average(data)

        time.sleep(0.5)
        result = self.dev.set_gain(100)
        result, data = self.dev.grab_pipe()
        avg_low_gain = numpy.average(data)

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

        forc_res = self.dev.close_port()
        self.assertTrue(self.dev.close_pipe())

    def test_openwriteclose_gain(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 2048)

        self.assertTrue(self.dev.open_write_close("gain 187"))
        result, data = self.dev.grab_pipe()
        avg_default = numpy.average(data)

        self.assertTrue(self.dev.open_write_close("gain 100"))
        result, data = self.dev.grab_pipe()
        avg_low_gain = numpy.average(data)

        gain_diff_threshold = 1000
        gain_diff = abs(avg_low_gain - avg_default)
        self.assertGreater(gain_diff, gain_diff_threshold)

        self.assertTrue(self.dev.close_pipe())


    def test_offset(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 2048)

        self.assertTrue(self.dev.open_write_close("offset 0"))
        result, data = self.dev.grab_pipe()
        avg_default = numpy.average(data)

        self.assertTrue(self.dev.open_write_close("offset 255"))
        result, data = self.dev.grab_pipe()
        avg_high_offset = numpy.average(data)

        self.assertGreater(avg_default, avg_high_offset)

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

