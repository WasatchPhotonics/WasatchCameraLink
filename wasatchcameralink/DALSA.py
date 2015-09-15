""" Wasatch Photonics device communication over camera link DALSA cards.

Uses a modified version of the Sapera .NET example code to read single
lines of data from the device at a time.
"""

import os
import sys
import struct
import logging
        
import subprocess
from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

class SaperaCMD(object):
    """ Base class that calls the sapera grab console modified
    demonstration program with the supplied parameters and returns the
    data.
    """
    def __init__(self):
        super(SaperaCMD, self).__init__()
        self.card = None
        self.ccf = None
        self.command = "grab"
        self.index = "0"

        # Disable startupinfo if you need to see the sapera application
        # in the windowing system
        self.startupinfo = subprocess.STARTUPINFO()
        self.startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

    def set_pixel_size(self):
        """ Process the specified ccf file, store the number of pixels.
        """
        path, file_name = os.path.split(__file__)
        prefix = "%s\\GrabConsole\\CSharp\\bin\\Debug\\" % path
        ccf_file = "%s\\%s.ccf" % (prefix, self.ccf)

        log.debug("Find ccf file: %s" % ccf_file)
        try:
            in_file = open(ccf_file)
            for line in in_file.readlines():
                if "Crop Width" in line:
                    line = line.replace("\n", "")
                    self.pixels = int(line.split("=")[-1])
                    log.info("pixels is [%s]" % self.pixels)

        except:
            log.critical("CCF proccessing" + str(ccf_file) + \
                          str(sys.exc_info()))
            return 0, "fail"

    def setup_pipe(self):
        """ Create a pipe connection to the csharp version of the single
        line grabber on the console example from Dalsa.
        """
        log.info("Setup pipe device")

        # Get the location of this module on disk, use it to generate
        # the absolute pathname to the .net application
        path, file_name = os.path.split(__file__)

        prefix = "%s\\GrabConsole\\CSharp\\bin\\Debug\\" % path
        cmd_path = "%s\\SapNETCSharpGrabConsole.exe" % prefix

        ccf_file = "%s\\%s.ccf" % (prefix, self.ccf)

        log.info("open %s, %s", cmd_path, ccf_file)
            
        opts = [cmd_path, self.command, self.card, self.index, ccf_file]

        try:
            self.pipe = Popen(opts, 
                              stdin=PIPE, stdout=PIPE,
                              startupinfo=self.startupinfo)
        except:
            log.critical("Failure to setup pipe: " + str(sys.exc_info()))
            return False

        return True


    def grab_pipe(self):
        """ Issue a newline, get a line of data over the pipes.
        """

        self.trigger_snap()
        self.trigger_save()
            
        self.trigger_next() # just hit enter

        result, data = self.grab_data()

        self.trigger_repeat()

        return result, data


    def trigger_repeat(self):
        """ Convenience function to illustrate the order of operations.
        """
        log.debug("WR enter to trigger repeat")
        self.pipe.stdin.write("\n")
        line = self.pipe.stdout.readline().replace('\n', '')
        log.debug("READ " + str(line))
        log.debug("\n")

    def trigger_next(self):
        """ Convenience function to illustrate the order of operations.
        """
        line = self.pipe.stdout.readline().replace('\n', '')
        log.debug("READ " + str(line))
        log.debug("\n")

    def trigger_save(self):
        """ Convenience function to illustrate the order of operations.
        """
        line = self.pipe.stdout.readline().replace('\n', '')
        log.debug("READ " + str(line))
        log.debug("WR enter to trigger save")
        log.debug("\n")
        self.pipe.stdin.write("\n")

    def trigger_snap(self):
        """ Convenience function to illustrate the order of operations.
        """
        line = self.pipe.stdout.readline().replace('\n', '')
        log.debug("READ " + str(line))
        log.debug("WR enter to trigger snap")
        log.debug("\n")
        self.pipe.stdin.write("\n")

    def grab_data(self, in_filename="test.raw"):
        """ Read from the given raw pixel file as extracted from the
        DALSA command line example program. Return list of pixel values
        after unpacking.
        """
        img_data = []
        try:
            in_file = open(in_filename, 'rb')
            all_data = in_file.read()
            in_file.close()
            pos = 0
            # 2048 pixels of data, 4096 bytes
            byte_size = (self.pixels * 2) - 1
            while pos < byte_size:
                pixel_one = all_data[pos] + all_data[pos+1]
                data_pak = struct.unpack("H", pixel_one)
                img_data.append(data_pak[0])
                pos += 2

            return 1, img_data

        except:
            log.critical("Problem reading " + str(in_filename) + \
                          str(sys.exc_info()))
            return 0, "fail"

        return 0, "done"


    def close_pipe(self):
        """ write multiple q's to close the stdout pipe.
        """
        log.info("Close pipe")
        # write a bunch of q's and read the lines to close it out
        try:
            for i in range(10):
                log.debug("WR q" + str(i))
                self.pipe.stdin.write("q\n")
                line = self.pipe.stdout.readline().replace('\n','')
                
            self.pipe.stdin.flush()
            self.pipe.stdout.flush()
        except:
            log.warn("close pipe fail: " + str(sys.exc_info()))

        return 1


class Cobra(SaperaCMD):
    """ Use a Dalsa frame grabber and the stdin/stdout customized
    example from Sapera.
    """
    def __init__(self, card="Xcelera-CL_LX1_1", ccf="cobra"):
        super(Cobra, self).__init__()
        log.debug("Cobra Startup")

        self.card = card
        self.ccf = ccf

        self.set_pixel_size()


class BaslerSprint4K(SaperaCMD):
    """ Use a Dalsa frame grabber and the stdin/stdout customized
    example from Sapera.
    """
    def __init__(self, card="Xcelera-CL_LX1_1", ccf="BaslerSprint4K"):
        super(BaslerSprint4K, self).__init__()
        log.debug("Basler sprint 4k Startup")

        self.card = card
        self.ccf = ccf

        self.set_pixel_size()
