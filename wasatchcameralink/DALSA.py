""" Wasatch Photonics device communication over camera link DALSA cards.

Uses a modified version of the Sapera .NET example code to read single
lines of data from the device at a time.
"""

import sys
import struct
import logging
        
import subprocess
from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

class Cobra(object):
    """ Use a Dalsa frame grabber and the stdin/stdout customized
    example from Sapera.
    """
    def __init__(self):
        super(Cobra, self).__init__()
        log.debug("Cobra Startup")


    def setup_pipe(self):
        """ Create a pipe connection to the csharp version of the single
        line grabber on the console example from Dalsa.
        """
        log.info("Setup pipe device")
        prefix = "wasatchcameralink\\GrabConsole\\CSharp\\bin\\Debug\\"

        cmd = "%s\\SapNETCSharpGrabConsole.exe" % prefix
        ccf = "%s\\prcinternal.ccf" % prefix
        log.debug("open %s, %s", cmd, ccf)
        try:
            opts = [cmd, 'grab', 'Xcelera-CL_LX1_1', '0', ccf]
            self.pipe = Popen(opts, stdin=PIPE, stdout=PIPE)
        except:
            log.critical("Failure to setup pipe: " + str(sys.exc_info()))
            return False

        return True


    def grab_pipe(self):
        """ Issue a newline, get a line of data over the pipes.
        """

        line = self.pipe.stdout.readline().replace('\n', '')
        log.info("READ " + str(line))
        log.info("WR enter to trigger snap")
        log.info("\n")
        self.pipe.stdin.write("\n")

        line = self.pipe.stdout.readline().replace('\n', '')
        log.info("READ " + str(line))
        log.info("WR enter to trigger save")
        log.info("\n")
        self.pipe.stdin.write("\n")

        line = self.pipe.stdout.readline().replace('\n', '')
        log.info("READ " + str(line))
        log.info("\n")

        #time.sleep(1)
        log.info("Open file")
        result, data = self.grab_data("test.raw")
        log.info(str(data[0:3]))
        log.info("Done file")
        #time.sleep(1)

        log.info("WR enter to trigger repeat")
        self.pipe.stdin.write("\n")
        line = self.pipe.stdout.readline().replace('\n', '')
        log.info("READ " + str(line))
        log.info("\n")

        return result, data

    def grab_data(self, in_filename="tools\\test.raw"):
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
            while pos < 4095:
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
                log.info("WR q" + str(i))
                self.pipe.stdin.write("q\n")
                line = self.pipe.stdout.readline().replace('\n','')
                
            self.pipe.stdin.flush()
            self.pipe.stdout.flush()
        except:
            log.warn("close pipe fail: " + str(sys.exc_info()))

        return 1
