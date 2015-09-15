""" simulated cameralink device test cases
"""

import unittest

from wasatchcameralink import simulation

class TestSimulatedSpectra(unittest.TestCase):

    def setUp(self):
        self.dev = simulation.SimulatedSpectraDevice()

    def test_pipe_cycle(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 2048)

        self.assertTrue(self.dev.close_pipe())

    def test_pipe_random_pattern(self):
        self.assertTrue(self.dev.setup_pipe())

        result, data = self.dev.grab_pipe()
        self.assertTrue(result)
        self.assertEqual(len(data), 2048)


        # Roll through a bunch of simulated acquisitions, repeat
        for i in range(500):
            result, data = self.dev.grab_pipe()

            # Psuedo-verify the randomness
            self.assertNotEqual(data[0], 0)
            self.assertNotEqual(data[-1], 0)

            self.assertNotEqual(data[0], data[-1])
            self.assertNotEqual(data[100], data[-100])


class TestSimulatedPipe(unittest.TestCase):
    
    def setUp(self):
        self.dev = simulation.SimulatedPipeDevice()

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
