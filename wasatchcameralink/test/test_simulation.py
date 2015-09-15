""" simulated pipe device test cases
"""

import unittest

from testfixtures import LogCapture

from linegrab.devices import SimulatedPipeDevice

class Test(unittest.TestCase):
    
    def setUp(self):
        self.dev = SimulatedPipeDevice()
        self.log_capture = LogCapture()
        self.log_name = "linegrab.devices"

    def tearDown(self):
        self.log_capture.uninstall()

    def test_log_captures(self):
        # verification of log matching functionality
        from logging import getLogger
        getLogger().info('a message')
        self.log_capture.check(('root', 'INFO', 'a message'))

    def test_module_logging(self):
        self.assertTrue(self.dev.setup_pipe())

        gr = self.log_name
        self.log_capture.check(
            (gr, "INFO", "Setup pipe device"),
            )

    def test_pipe_cycle(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 1024)

        self.assertTrue(self.dev.close_pipe())

    def test_pipe_test_pattern(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 1024)
        self.assertEqual(data[0], 0)
        self.assertEqual(data[1023], 1000)

        # Roll through half the test pattern
        for i in range(500):
            result, data = self.dev.grab_pipe()

        self.assertEqual(data[0], 500)
        self.assertEqual(data[1023], 1500)
   
        # roll through the rest of the test pattern, make sure it wraps 
        for i in range(500):
            result, data = self.dev.grab_pipe()
    
        self.assertEqual(data[0], 0)
        self.assertEqual(data[1023], 1000)

if __name__ == "__main__":
    unittest.main()
