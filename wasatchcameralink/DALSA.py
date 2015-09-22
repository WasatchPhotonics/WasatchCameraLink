""" Wasatch Photonics device communication over camera link DALSA cards.

Uses a modified version of the Sapera .NET example code to read single
lines of data from the device at a time.
"""


import os
import sys
import time
import serial
import struct
import logging
        
import subprocess
from subprocess import Popen, PIPE

log = logging.getLogger(__name__)

COM_PORT = 5 # windows reported number 

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

        self.stop_sapgrab()

    def stop_sapgrab(self):
        """ Kill any running instances of the sapera grab application.
        No clean, no confirmation, just kill.
        """
        # > /NUL is to keep the 'sent termination...' message from printing
        # Would be nice to capture it and send it to log
        task_cmd = "taskkill /F /IM SapNETCSharpGrabConsole.exe"
        grab_kill = '''"%s 1> NUL 2> NUL"''' % task_cmd
        result = os.system(grab_kill)
        print "Kill result: %s" % result
        return True


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
    example from Sapera. Provide device control wrappers around the
    serial port interface.
    """
    def __init__(self, card="Xcelera-CL_LX1_1", ccf="cobra"):
        super(Cobra, self).__init__()
        log.debug("Cobra Startup")

        self.card = card
        self.ccf = ccf

        self.set_pixel_size()
        #self.open_port()
        #self.start_scan()
        #self.close_port()

    def start_scan(self):
        """ Issue the required startup parameters to set the device in
        internal triggered mode.
        """
        if not self.write_command("init"):
            return 0
        if not self.write_command("ats 0"):
            return 0
        if not self.write_command("lsc 1"):
            return 0
        return 1

    def set_gain(self, gain):
        """ write the gain value over serial.
        """
        #return self.open_write_close("gain %s" % gain)
        return self.write_command("gain %s" % gain)

    def set_offset(self, offset):
        """ write the offset value over serial.
        """
        #return self.open_write_close("offset %s" % offset)
        return self.write_command("offset %s" % offset)

    def open_write_close(self, command):
        """ Open the serial port, write the command, close it.
        """
        self.open_port()
        self.write_command(command)
        self.close_port()
        return True

    def close_port(self):
        try:
            self.serial_port.close()
            return 1
        except:
            log.critical("Problem closing port: " + str(sys.exc_info()))
        return 0


    def open_port(self):
        """ Connect to the serial port for the Cobra cameralink board,
        verify the version number is as expected.  """

        com_port = COM_PORT - 1 # zero based in python, 1 based in
                                # windows
        self.serial_port = serial.Serial()
        self.serial_port.baudrate = 9600
        self.serial_port.port = int(com_port)
        self.serial_port.timeout = 1
        self.serial_port.writeTimeout = 1

        try:
            result = self.serial_port.close()  # yes, close before open
            result = self.serial_port.open()
        except:
            log.critical("Problem close/open: " + str(sys.exc_info()))
            return 0
            
        return 0


    def write_command(self, command, read_bytes=7):
        """ append required control characters to the specified command,
        write to the device over the serial port, and expect OK from the
        device.
        """

        try:
            fin_command = command + '\r'
            log.debug("send command [%s]" % fin_command)
            result = self.serial_port.write(str(fin_command))
            self.serial_port.flush()
        except:
            log.critical("Problem writing %s" % command)
            log.critical("%s", sys.exc_info())
            return 0

        try:
            result = self.serial_port.read(read_bytes)
            log.debug("Serial read result [%r]" % result)
            if "<ok>" not in result:
                log.critical("Command failure: %s,%s" %(command,result))
                return 0
        except:
            log.critical("Problem reading from com " + str(com_port))
            log.critical(str(sys.exc_info()))
            return -2

        log.debug("command write")
        return 1


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
