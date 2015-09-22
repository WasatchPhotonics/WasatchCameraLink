""" Real and simulated devices for providing stdin/stdout pipe based
communication with camera control devices.
"""

import os
import numpy
import logging

log = logging.getLogger(__name__)


class SimulatedPipeDevice(object):
    """ Use the pipe device interface, return a cycling test pattern of
    data.
    """

    def __init__(self, pattern_jump=1, top_level=1000):
        #log.debug("Startup")
        self.pattern_position = 0
        self.data_length = 1024
        self.top_level = top_level
        self.pattern_jump = pattern_jump

    def setup_pipe(self):
        #log.info("Setup pipe device")
        return True

    def grab_pipe(self):
        """ Create a cycling test pattern based on the current position
        """
        #log.debug("Grab pipe")
        start = self.pattern_position 
        end = self.pattern_position + self.top_level
        data = numpy.linspace(start, end, 1024)

        self.pattern_position += self.pattern_jump
        if self.pattern_position >= self.top_level:
            self.pattern_position = 0

        return True, data

    def close_pipe(self):
        #log.info("Close pipe device")
        self.pattern_position = 0
        return True
        
    def set_gain(self, gain):
        """ Placeholder function to simulate settings change
        """    

    def set_offset(self, offset):
        """ Placeholder function to simulate settings change
        """    


class SimulatedSpectraDevice(SimulatedPipeDevice):
    """ Given a class of spectra, create a default waveform, and return
    randomized data along that waveform.
    """
    def __init__(self, spectra_type="raman"):
        super(SimulatedSpectraDevice, self).__init__()
        self.spectra_type = spectra_type

        if self.spectra_type == "raman":
            self.waveform = self.generate_raman()

    def generate_raman(self):
        self.raman_peaks = 10
        self.noise_floor = 50
        self.noise_ceiling = 150
        nru = numpy.random.uniform

        low_data = nru(100, 200, 2048)
        blk = numpy.linspace(0, 0, 2048)

        # up to half the width, add a value that is at least greater
        # than a threshold, then move the threshold up
        width = 10
    
        half = width / 2
        min_gap = 10


        for position in range(self.raman_peaks):

            # get a random peak within the range
            peak_pos = int(nru(100, 2037, 1))
            peak_height = int(nru(500, 1000, 1))

            floor = peak_height + min_gap
            peak_x = peak_pos

            for item in range(half):
                new_floor = floor + min_gap
                new_height = nru(floor, new_floor, 1)
                new_height = int(new_height)
                floor = new_floor
                blk[peak_x] = new_height
                peak_x += 1
    
            for item in range(half):
                new_floor = floor - min_gap
                new_height = nru(floor, new_floor, 1)
                new_height = int(new_height)
                floor = new_floor
                blk[peak_x] = new_height
                peak_x += 1
    
        self.base_data = low_data + blk


    def grab_pipe(self):
        """ Apply randomness at each grab.
        """
        
        nru = numpy.random.uniform
        noise_data = nru(self.noise_floor, self.noise_ceiling, 2048)
        new_data = self.base_data + noise_data
        test_data = numpy.array(new_data).astype(int)
        return True, test_data
        

class SimulatedCobraSLED(SimulatedPipeDevice):
    """ Display a sled output based stored data. Apply noise and
    other shifts based on sent commands.
    """
    def __init__(self, sled_type="single"):
        super(SimulatedCobraSLED, self).__init__()
        self.sled_type = sled_type

        if self.sled_type == "single":
            self.base_data = self.load_single_sled()

        self.noise_floor = 0
        self.noise_ceiling = 10

    def load_single_sled(self, filename="cobra_singlesled.txt"):
        """ Read from an example file, use as baseline data.
        """
       
        # Stored txt is in unknown path at runtime 
        path, file_name = os.path.split(__file__)
        filen = "%s/%s" % (path, filename)
        return numpy.loadtxt(filen, delimiter=",")

    def grab_pipe(self):
        """ Apply randomness at each grab.
        """
        
        nru = numpy.random.uniform
        noise_data = nru(self.noise_floor, self.noise_ceiling, 2048)
        new_data = self.base_data + noise_data
        test_data = numpy.array(new_data).astype(int)
        return True, test_data
            
    def set_gain(self, gain):
        """ Reload the base data, multiply by the gain for easily
        visualizable results.
        """
        new_data = self.base_data + gain
        self.base_data = new_data
        pass
            
    def set_offset(self, offset):
        """ Reload the base data, add by the (offset*10) for easily
        visualizable results.
        """
        new_data = self.base_data + offset
        self.base_data = new_data

    def open_port(self):
        """ simulated serial control
        """
        return True

    def close_port(self):
        """ simulated serial control
        """
        return True

    def start_scan(self):
        """ simulated serial control
        """
        return True
