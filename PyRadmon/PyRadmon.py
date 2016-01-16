#!/usr/bin/python

from collections import deque
import logging
import math
import pyaudio
import random
import serial
import socket
import struct
import sys, os
import threading, thread
import time, datetime

##############################################################################
#  pyRadMon - logger for Geiger counters                                     #
#  Original Copyright 2013 by station pl_gdn_1                               #
#  Copyright 2014 by Auseklis Corporation, Richmond, Virginia, U.S.A.        #
#  Copyright 2015-2016 by Thibmo at Radmon.org                               #
#                                                                            #
#  This file is part of The PyRadMon Project                                 #
#  https://sourceforge.net/p/pyradmon-reborn                                 #
#                                                                            #
#  PyRadMon is free software: you can redistribute it and/or modify it under #
#  the terms of the GNU General Public License as published by the Free      #
#  Software Foundation, either version 3 of the License, or (at your option) #
#  any later version.                                                        #
#                                                                            #
#  PyRadMon is distributed in the hope that it will be useful, but WITHOUT   #
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or     #
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for #
#  more details.                                                             #
#                                                                            #
#  You should have received a copy of the GNU General Public License         #
#  along with PyRadMon.  If not, see <http://www.gnu.org/licenses/>.         #
#                                                                            #
#  @license GPL-3.0+ <http://spdx.org/licenses/GPL-3.0+>                     #
##############################################################################
#  version is a.b.c, change in a or b means new functionality/bugfix,        #
#  change in c = bugfix                                                      #
#  do not uncomment line below, it's currently used in HTTP headers          #
VERSION = "1.2.0"
#  To see your online los, report a bug or request a new feature, please     #
#  visit http://www.radmon.org and/or https://sourceforge.net/p/pyradmon     #
##############################################################################

# Set logger default info
logging.basicConfig(filename = "pyradmon_log.log", filemode = "a",
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt = "%d/%m/%Y %H:%M:%S %p")
logger = logging.getLogger("PyRadmon (Audio)")
logger.setLevel(logging.DEBUG)

##############################################################################
# Part 1 - configuration procedures
#
# Read configuration from file + constants definition
##############################################################################
class config():
    # Used as enums
    UNKNOWN = 0
    DEMO = 1
    MYGEIGER = 2
    GMC = 3
    NETIO = 4
    AUDIO = 5

    def __init__(self):
        # Define constants
        self.CONFIGFILE = "config.txt"
        self.UNKNOWN = 0
        self.DEMO = 1
        self.MYGEIGER = 2
        self.GMC = 3
        self.NETIO = 4
        self.AUDIO = 5
        self.user = "not_set"
        self.password = "not_set"
        self.portName = None
        self.portSpeed = 2400
        self.timeout = 40 # not used for now
        self.protocol = self.UNKNOWN
        self.deviceIndex = 0

    def readConfig(self):
        print "Reading configuration:\r\n\t"
        logger.info("Reading configuration")
        # If file is present then try to read configuration from it
        try:
            f = open(self.CONFIGFILE)
            line = " "

            # Analyze file line by line, format is parameter=value
            while(line):
                line = f.readline()
                params = line.split("=")

                if len(params) == 2:
                    parameter = params[0].strip().lower()
                    value = params[1].strip()

                    if parameter == "user":
                        self.user = value
                        print "\tUser name configured\r\n\t"
                        logger.info("User name configured")
                    elif parameter == "password":
                        self.password = value
                        print "\tPassword configured\r\n\t"
                        logger.info("Password configured")
                    elif parameter == "serialport":
                        self.portName = value
                        print "\tSerial port name configured\r\n\t"
                        logger.info("Serial port name configured")
                    elif parameter == "speed":
                        self.portSpeed = int(value)
                        print "\tSerial port speed configured\r\n\t"
                        logger.info("Serial port speed configured")
                    elif parameter == "device":
                        self.deviceIndex = int(value)
                        print "\tDevice number configured\r\n\t"
                        logger.info("Device number configured")
                    elif parameter == "protocol":
                        value = value.lower()

                        if value == "mygeiger":
                            self.protocol = self.MYGEIGER
                        elif value == "demo":
                            self.protocol = self.DEMO
                        elif value == "gmc":
                            self.protocol = self.GMC
                        elif value == "netio":
                            self.protocol = self.NETIO
                        elif value == "audio":
                            self.protocol = self.AUDIO
                        else:
                            self.protocol = self.UNKNOWN

                    if self.protocol != self.UNKNOWN:
                        print "\tProtocol configured\r\n\t"
                        logger.info("Protocol configured")
                # End of if
            # End of while

            f.close()
        except Exception as e:
            print "\tFailed to read configuration file:\r\n\t" + str(e) + "\r\nExiting\r\n"
            logger.exception("Failed to read configuration file: " + str(e))
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            exit(1)

        # well done, configuration is ready to use
        print ""

################################################################################
# Part 2 - Geiger counter communication
#
# It should be easy to add different protocol by simply
# creating new class based on baseGeigerCommunication, as it's done in
# classes Demo and myGeiger
################################################################################
class baseGeigerCommunication(threading.Thread):
    def __init__(self, cfg):
        super(baseGeigerCommunication, self).__init__()
        self.sPortName = cfg.portName
        self.sPortSpeed = cfg.portSpeed
        self.timeout = cfg.timeout
        self.stopwork = 0
        self.queue = deque()
        self.queueLock = 0
        self.is_running = 1
        self.name = "baseGeigerCommunication"

    def run(self):
        try:
            print "Gathering data started => geiger 1\r\n"
            self.serialPort = serial.Serial(self.sPortName, self.sPortSpeed, timeout = 1)
            self.serialPort.flushInput()
            self.initCommunication()

            while(self.stopwork == 0):
                result = self.getData()

                while(self.queueLock == 1):
                    print "Geiger communication: queue locked! => geiger 1\r\n"
                    logger.warning("Geiger communication: queue locked! => geiger 1")
                    time.sleep(0.5)

                self.queueLock = 1
                self.queue.append(result)
                self.queueLock = 0
                print "Geiger sample => geiger 1:\tCPM =", result[0], "\t", str(result[1])

            self.serialPort.close()
            print "Gathering data from Geiger stopped => geiger 1\r\n"
        except serial.SerialException as e:
            print "Problem with serial port => geiger 1:\r\n\t", str(e), "\r\nExiting\r\n"
            logger.exception("Problem with serial port => geiger 1: " + str(e))
            self.stop()
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

    def initCommunication(self):
        print "Initializing geiger communication => geiger 1\r\n"

    def sendCommand(self, command):
        self.serialPort.flushInput()
        self.serialPort.write(command)
        # Assume that device responds within 0.5s
        time.sleep(0.5)
        response = ""

        while(self.serialPort.inWaiting() > 0 and self.stopwork == 0):
            response = response + self.serialPort.read()

        return response

    def getData(self):
        cpm = 25
        utcTime = datetime.datetime.utcnow()
        data = [cpm, utcTime]
        return data

    def stop(self):
        self.stopwork = 1
        self.queueLock = 0
        self.is_running = 0

    def getResult(self):
        # Check if we have some data in queue
        if len(self.queue) > 0:
            # Check if it's safe to process queue
            while(self.queueLock == 1):
                print "getResult: queue locked! => geiger 1\r\n"
                logger.warning("getResult: queue locked! => geiger 1")
                time.sleep(0.5)

            # Put lock so measuring process will not interfere with queue,
            # processing should be fast enought to not break data acquisition from geiger
            self.queueLock = 1
            cpm = 0

            # Now get sum of all CPM's
            for singleData in self.queue:
                cpm = cpm + singleData[0]

            # And divide by number of elements to get mean value, 0.5 is for rounding up/down
            cpm = int((float(cpm) / len(self.queue)) + 0.5)
            # Report with latest time from quene
            utcTime = self.queue.pop()[1]
            # Clear queue and remove lock
            self.queue.clear()
            self.queueLock = 0
            data = [cpm, utcTime]
        else:
            # No data in queue, return invalid CPM data and current time
            data = [-1, datetime.datetime.utcnow()]

        return data

class Demo(baseGeigerCommunication):
    def run(self):
        print "Gathering data started => geiger 1\r\n"

        while(self.stopwork == 0):
            result = self.getData()

            while(self.queueLock == 1):
                print "Geiger communication: queue locked! => geiger 1\r\n"
                logger.warning("Geiger communication: queue locked! => geiger 1")
                time.sleep(0.5)

            self.queueLock = 1
            self.queue.append(result)
            self.queueLock = 0
            print "Geiger sample => geiger 1:\t", result, "\r\n"

        print "Gathering data from Geiger stopped => geiger 1\r\n"

    def getData(self):
        for i in range(0, 5):
            time.sleep(1)

        cpm = random.randint(5, 40)
        utcTime = datetime.datetime.utcnow()
        data = [cpm, utcTime]
        return data

class myGeiger(baseGeigerCommunication):
    def getData(self):
        cpm = -1

        try:
            # Wait for data
            while(self.serialPort.inWaiting() == 0 and self.stopwork == 0):
                time.sleep(1)

            time.sleep(0.1) # Just to ensure all CPM bytes are in serial port buffer
            # Read all available data
            x = ""

            while(self.serialPort.inWaiting() > 0 and self.stopwork == 0):
                x = x + self.serialPort.read()

            if len(x) > 0:
                cpm = int(x)

            utcTime = datetime.datetime.utcnow()
            data = [cpm, utcTime]
            return data
        except Exception as e:
            print "\r\nProblem in getData procedure (disconnected USB device?) => geiger 1:\r\n\t", str(e), "\r\nExiting\r\n"
            logger.exception("Problem in getData procedure (disconnected USB device?) => geiger 1: " + str(e))
            self.stop()
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

class gmc(baseGeigerCommunication):
    def initCommunication(self):
        print "Initializing GMC protocol communication => geiger 1\r\n"
        logger.info("Initializing GMC protocol communication => geiger 1")
        # Get firmware version
        response = self.sendCommand("<GETVER>>")

        if len(response) > 0:
            print "Found GMC-compatible device, version => geiger 1: ", response, "\r\n"
            # Disable heartbeat, we will request data from script
            self.sendCommand("<HEARTBEAT0>>")
            print "Please note data will be acquired once per 5 seconds => geiger 1\r\n"
            # Update the device time
            unitTime = self.sendCommand("<GETDATETIME>>")
            print "Unit shows time as => geiger 1: ", unitTime, "\r\n"
            print "<SETDATETIME[" + time.strftime("%y%m%d%H%M%S") + "]>>"
        else:
            print "No response from device => geiger 1\r\n"
            logger.error("No response from device => geiger 1")
            self.stop()
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

    def getData(self):
        cpm = -1

        try:
            # Wait, we want sample every 30s
            for i in range(0,3):
                time.sleep(1)

            # Cend request
            response = self.sendCommand("<GETCPM>>")

            if len(response) == 2:
                # Convert bytes to 16 bit int
                cpm = ord(response[0]) * 256 + ord(response[1])
            else:
                print "Unknown response to CPM request, device is not GMC-compatible? => geiger 1\r\n"
                logger.error("Unknown response to CPM request, device is not GMC-compatible? => geiger 1")
                self.stop()
                logger.shutdown()
                sys.exit(1)

            utcTime = datetime.datetime.utcnow()
            data = [cpm, utcTime]
            return data
        except Exception as e:
            print "\r\nProblem in getData procedure (disconnected USB device?) => geiger 1:\r\n\t", str(e), "\r\nExiting\r\n"
            logger.exception("Problem in getData procedure (disconnected USB device?) => geiger 1: " + str(e))
            self.stop()
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

class netio(baseGeigerCommunication):
    def getData(self):
        cpm = -1

        try:
            # We want data only once per 30 seconds, ignore rest it's averaged for 60 seconds by device anyway
            for i in range(0, 30):
                time.sleep(1)

            # Wait for data, should be already there (from last 30s)
            while (self.serialPort.inWaiting() == 0 and self.stopwork == 0):
                time.sleep(0.5)

            time.sleep(0.1) # just to ensure all CPM bytes are in serial port buffer
            # Read all available data do not stop receiving unless it ends with \r\n
            x = ""

            while(x.endswith("\r\n") == False and self.stopwork == 0):
                while(self.serialPort.inWaiting() > 0 and self.stopwork == 0):
                    x = x + self.serialPort.read()

            # If CTRL+C pressed then x can be invalid so check it
            if x.endswith("\r\n"):
                # We want only latest data, ignore older
                tmp = x.splitlines()
                x = tmp[len(tmp) - 1]
                cpm = int(x)

            utcTime = datetime.datetime.utcnow()
            data = [cpm, utcTime]
            return data
        except Exception as e:
            print "\r\nProblem in getData procedure (disconnected USB device?) => geiger 1:\r\n\t", str(e), "\r\nExiting\r\n"
            logger.exception("Problem in getData procedure (disconnected USB device?) => geiger 1: " + str(e))
            self.stop()
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

    def initCommunication(self):
        print "Initializing NetIO => geiger 1\r\n"
        logger.info("Initializing NetIO => geiger 1")
        # Send "go" to start receiving CPM data
        response = self.sendCommand("go\r\n")
        print "Please note data will be acquired once per 30 seconds => geiger 1\r\n"

################################################################################
# Part 2b - audio geiger handeler
################################################################################
# If the noise was longer than this many blocks, it's not a 'tap'
def get_rms(block):
    """
      RMS amplitude is defined as the square root of the mean over time of the square of the amplitude.
      So we need to convert this string of bytes into a string of 16-bit samples...
      We will get one short out for each two chars in the string.
    """
    count = len(block) / 2
    format = "%dh"%(count)
    shorts = struct.unpack(format, block)
    # Iterate over the block.
    sum_squares = 0.0

    for sample in shorts:
        # Sample is a signed short in +/- 32768. Normalize it to 1.0
        n = sample * (1.0 / 32768.0)
        sum_squares += n * n

    return math.sqrt(sum_squares / count)

class audioCommunication(threading.Thread):
    def __init__(self, cfg):
        super(audioCommunication, self).__init__()
        self.initCommunication()
        self.timeout = cfg.timeout
        self.stopwork = 0
        self.queue = deque()
        self.queueLock = 0
        self.is_running = 1
        self.pa = pyaudio.PyAudio()
        self.device_index = cfg.deviceIndex
        self.device_Channels = self.pa.get_device_info_by_index(self.device_index)['maxInputChannels']
        self.noisycount = 0
        self.bSquelchIoerror = int(1) != 0
        self.name = "audioCommunication"

    def initCommunication(self):
        print "Initializing audio communication => geiger 1\r\n"
        logger.info("Initializing audio communication => geiger 1")

    def run(self):
        try:
            print "Gathering data started => geiger 1\r\n"

            while(self.stopwork == 0):
                result = self.getData()

                while(self.queueLock == 1):
                    print "Geiger communication: quene locked! => geiger 1\r\n"
                    logger.warning("Geiger communication: quene locked! => geiger 1")
                    time.sleep(0.5)

                self.queueLock = 1
                self.queue.append(result)
                self.queueLock = 0
                print "Geiger sample => geiger 1:\tCPM =", result[0], "\t", str(result[1]), "\r\n"

            print "Gathering data from Geiger stopped => geiger 1\r\n"
        except Exception as e:
            print "Problem with audio port => geiger 1:\r\n\t", str(e), "\r\nExiting\r\n"
            logger.exception("Problem with audio port => geiger 1: " + str(e))
            self.stop() # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

    def getData(self):
        if self.device_Channels > 2:
            self.device_Channels = 2

        self.stream = self.pa.open(format = pyaudio.paInt16,
                                   channels = self.device_Channels,
                                   rate = 44100,
                                   input = True,
                                   input_device_index = self.device_index,
                                   start = True,
                                   frames_per_buffer = int(44100 * 0.05))

        for i in range(0, int(44100 / 1024 * 30)):
            try:
                if not self.stream: break

                block = self.stream.read(1024)
            except (pyaudio.paInputOverflowed, IOError,):
                """
                  Buffer overflows are a real problem in pyaudio depending on the choice of fRate and CHUNK.
                  Signal them to the user, but ignore them - play with fRate and CHUNK until they are at a minimum
                """
                if self.is_running and not self.bSquelchIoerror:
                    print "paInputOverflow on audio port => %d"
                    logger.error("paInputOverflow on audio port => %d")

                continue
            except Exception as ex:
                print "Problem with audio port => 1\r\n\t", str(ex), "\r\n\tExiting\r\n\t"
                logger.exception("Problem with serial port => geiger 1: " + str(ex))

                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None

                self.stop()
                # Set EOL for log
                logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
                logging.shutdown()
                sys.exit(1)

            amplitude = get_rms(block)

            if amplitude > 0.010:
                # Noisy block
                self.noisycount += 1

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.noisycount >= 0:
            cpm = self.noisycount * (60 / 30)
            self.noisycount = 0

        utcTime = datetime.datetime.utcnow()
        data = [cpm, utcTime]
        return data

    def stop(self):
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        self.stopwork = 1
        self.queueLock = 0
        self.is_running = 0

    def getResult(self):
        # Check if we have some data in queue
        if len(self.queue) > 0:
            # Check if it's safe to process queue
            while (self.queueLock == 1):
                print "getResult: quene locked! => geiger 1\r\n"
                logger.warning("getResult: queue locked! => geiger 1")
                time.sleep(0.5)

            """
              Put a lock so measuring process will not interfere with queue,
              processing should be fast enought to not break data acquisition from geiger
            """
            self.queueLock = 1
            cpm = 0

            # Now get sum of all CPM's
            for singleData in self.queue:
                cpm = cpm + singleData[0]

            # And divide by number of elements to get mean value, 0.5 is for rounding up/down
            cpm=int((float(cpm) / len(self.queue)) + 0.5)
            # Report with latest time from quene
            utcTime = self.queue.pop()[1]
            # Clear queue and remove lock
            self.queue.clear()
            self.queueLock = 0
            data = [cpm, utcTime]
        else:
            # No data in queue, return invalid CPM data and current time
            data = [-1, datetime.datetime.utcnow()]

        return data

################################################################################
# Part 3 - Web server communication
################################################################################
class webCommunication():
    HOST = "www.radmon.org"
    #HOST="127.0.0.1" # uncomment this for debug purposes on localhost
    PORT = 80

    def __init__(self, mycfg):
        self.user = mycfg.user
        self.password = mycfg.password

    def sendSample(self, sample):
        if not self.user or not self.password: return

        sampleCPM = sample[0]
        sampleTime = sample[1]
        # Format date and time as required
        dtime = sampleTime.strftime("%Y-%m-%d%%20%H:%M:%S")
        print "Connecting to server => geiger 1\r\n"
        logger.info("Connecting to server => geiger 1")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        url = "GET /radmon.php?user=" + self.user + "&password=" + self.password + "&function=submit&datetime=" + dtime+"&value=" + str(sampleCPM) + "&unit=CPM HTTP/1.1"
        request = url + "\r\nHost: www.radmon.org\r\nUser-Agent: pyRadMon " + VERSION + "\r\n\r\n"
        print "Sending average sample => geiger 1: ", str(sampleCPM), " CPM\r\n"

        try:
            s.connect((self.HOST, self.PORT))
            s.settimeout(10.0) # 10 seconds to timeout, this will prevent crash
            data = None
            doneSend = False
            s.send(request)
            time.sleep(0.5)
            data = s.recv(1024)
            time.sleep(0.5)

            for i in range(0, 10):
                if doneSend is False:
                    if data is not None:
                        httpResponse = str(data).splitlines()[0]
                        print "Server response => geiger 1: ", httpResponse, "\r\n"
                        logger.info("Server response => geiger 1: " + httpResponse)

                        if "incorrect" in data.lower():
                            print "You are using incorrect user/password combination => geiger 1!\r\n"
                            logger.error("You are using incorrect user/password combination => geiger 1!")
                            geigerCommunication.stop()
                            logging.shutdown()
                            sys.exit(1)

                        doneSend = True
        except Exception as ex:
            print "Could not communicate with the Server, timeout reached. => geiger 1: ", ex, "\r\n"
            logger.exception("Could not communicate with the Server, timeout reached. => geiger 1: " + str(ex))
        finally:
            s.close()

################################################################################
# Main code
################################################################################
def main():
    """
      Main loop is in while loop.
      Check if file exists, if not, create one and exit
    """
    if (os.path.isfile("config.txt") == 0):
        print "\tNo configuration file, creating default one.\r\n\t"

        try:
            f = open("config.txt", 'w')
            f.write("# Parameter names are not case-sensitive\r\n")
            f.write("# Parameter values are case-sensitive\r\n")
            f.write("user=test_user\r\n")
            f.write("password=test_password\r\n")
            f.write("# Port is usually /dev/ttyUSBx in Linux and COMx in Windows\r\n")
            f.write("serialport=/dev/ttyUSB0\r\n")
            f.write("speed=2400\r\n")
            f.write("# Protocols: demo, mygeiger, gmc, netio, audio\r\n")
            f.write("protocol=demo\r\n")
            f.write("# In case of audio, input the device number here, default is 0.\r\n")
            p = pyaudio.PyAudio()

            # For each audio device, determine if is an input or an output and add it to the appropriate list and dictionary
            for i in range (0, p.get_device_count()):
                dev = p.get_device_info_by_index(i)

                if dev['maxInputChannels'] > 0:
                    f.write("# " + str(i) + " - " + dev['name'] + " \r\n")
                else:
                    continue

            f.write("device=0\r\n")
            print "\tPlease open config.txt file using text editor and update configuration.\r\n"
        except Exception as e:
            print "\tFailed to create configuration file\r\n\t", str(e)
            logger.exception("Failed to create configuration file" + str(e))
        finally:
            time.sleep(1)
            p.terminate()
            f.close()

        # Set EOL for log
        logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
        logging.shutdown()
        sys.exit(1)
    else:
        # Create and read configuration data
        cfg = config()
        cfg.readConfig()

        # Create geiger communication object
        if cfg.protocol == config.MYGEIGER:
            print "Using myGeiger protocol => geiger 1\r\n"
            logger.info("Using myGeiger protocol => geiger 1")
            geigerCommunication = myGeiger(cfg)
        elif cfg.protocol == config.DEMO:
            print "Using Demo mode => geiger 1\r\n"
            logger.info("Using DEMO protocol => geiger 1")
            geigerCommunication = Demo(cfg)
        elif cfg.protocol == config.GMC:
            print "Using GMC protocol => geiger 1\r\n"
            geigerCommunication = gmc(cfg)
        elif cfg.protocol == config.NETIO:
            print "Using NetIO protocol => geiger 1\r\n"
            geigerCommunication = netio(cfg)
        elif cfg.protocol == config.AUDIO:
            print "Using audio protocol => geiger 1\r\n"
            geigerCommunication = audioCommunication(cfg)
        else:
            print "Unknown protocol configured, can't run => geiger 1\r\n"
            logger.error("Unknown protocol configured, can't run => geiger 1")
            # Set EOL for log
            logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
            logging.shutdown()
            sys.exit(1)

        try:
            # Create web server communication object
            webService = webCommunication(cfg)
            # Start measuring thread
            geigerCommunication.start()

            # Now send data to web site every 30 seconds
            while(geigerCommunication.is_running == 1):
                sample = geigerCommunication.getResult()

                if sample[0] != -1:
                    # Sample is valid, CPM !=-1
                    print "Average result => geiger 1:\tCPM =", sample[0], "\t", str(sample[1]), "\r\n"

                    try:
                        webService.sendSample(sample)
                    except Exception as e:
                        print "Error communicating server => geiger 1:\r\n\t", str(e), "\r\n"
                        logger.exception("Error communicating server => geiger 1: " + str(e))

                    print "Waiting 30 seconds => geiger 1\r\n"

                    """
                      Waiting 60x0.5 seconds, it has a better response when CTRL+C is used,
                      might be changed in future.
                    """
                    for i in range(0, 60):
                        time.sleep(0.5)
                else:
                    print "No samples in queue, waiting 5 seconds => geiger 1\r\n"

                    for i in range(0, 10):
                        time.sleep(0.5)

                    continue

        except KeyboardInterrupt as e:
            print "\r\nCTRL+C pressed, exiting program\r\n\t", str(e), "\r\n"
            logger.exception("CTRL+C pressed, exiting program: " + str(e))

        except SystemExit:
            print "\r\nSystem exit\r\n\t", str(e), "\r\n"
            logger.exception("System exit: " + str(e))

        except Exception as e:
            print "\r\nUnhandled error\r\n\t", str(e), "\r\n"
            logger.exception("Unhandled error: " + str(e))

        geigerCommunication.stop()
        # Threading fix
        print "Waiting and reap threads"
        logger.warning("Waiting and reap threads")
        time.sleep(1)

        for numThread in threading.enumerate():
            if numThread.isDaemon(): continue

            if numThread.getName() == 'MainThread': continue

            print "Stopping alive thread: ", numThread.getName(), "\r\n\t"
            logger.info("Stopping alive thread: " + numThread.getName())
            numThread.stop()
            time.sleep(1)

        logger.info("Shutting down application *Bye-bye*")
        # Set EOL for log
        logger.info("--------------------------------------- EOL ---------------------------------------\r\n")
        logging.shutdown()
        sys.exit(0)

if __name__ == '__main__':
    main()
