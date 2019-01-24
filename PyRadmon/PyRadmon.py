#!/usr/bin/env python3

# =====================================================================================================================
# Imports
#
from collections import deque;
import datetime;
from enum import Enum, unique;
import http.client as webClient;
import logging;
import math;
from numpy import mean, sqrt, square;
import os;
import random;
import struct;
import sys;
import threading;
import time;

try:
    import soundcard;
    SOUNDCARD_SUPPORT = True;
except ImportError:
    print('SoundCard module not found, disabeling functionality');
    SOUNDCARD_SUPPORT = False;
# End try

try:
    import serial;
    PYSERIAL_SUPPORT = True;
except ImportError:
    print('PySerial module not found, disabeling functionality');
    PYSERIAL_SUPPORT = False;
# End try

# =====================================================================================================================
# Module information
#
__author__ = 'Thimo Braker';
__status__ = 'development';
__version__ = '2.0.0';
__date__ = '2019-01-22';
__license__ = 'BEERWARE';

# =====================================================================================================================
# Constants
#
NEWLINE = "\n";
MSG_NEW_CONFIG = 'Creating a new default config file';
MSG_SHUTDOWN = 'Shutting down application *Bye-bye*';
MSG_END_OF_LOG = "--------------------------------------- EOL ---------------------------------------\n";
MSG_FMT_CONFIG_READ_FAIL = "Failed to read configuration file:\n%s\nExiting";
MSG_FMT_CONFIG_CREATE_FAIL = "Failed to create configuration file\n%s\nExiting";
MSG_FMT_SAS = 'Sending average sample: %s CPM';
MSG_FMT_WEB_ERROR = 'Could not communicate with the Server, timeout reached.: %s';
MSG_FMT_STOPPING_THREAD = 'Stopping alive thread: %s';
MSG_FMT_PROTOCOL = 'Using %s protocol';
MSG_FMT_DATA_STARTED = 'Data collection started for thread %s';
MSG_FMT_SYS_EXIT = "%s:\n%s";
MSG_FMT_EXCEPTION = "Unhandled exception:\n%s";
MSG_FMT_SERIAL_EXCEPTION = "Problem with serial port:\n%s\nExiting";
MSG_FMT_NEW_DATA = 'Received a new CPM value from the device: %s';
MSG_INCORRECT_CREDENTIALS = 'You are using incorrect user/password combination!';
MSG_WAIT_FOR_THREAD = 'Waiting a second for the device thread to catch up, then kill it';
MSG_QUEUE_LOCKED = 'Result queue is locked, retrying in 0.1 second';
MSG_CTRL_C_EXIT = 'CTRL+C pressed, exiting program';
MSG_SYS_EXIT = 'System exit';
RADMON_URL_FMT = '/radmon.php?user=%s&password=%s&function=submit&datetime=%s&value=%s&unit=CPM';

# =====================================================================================================================
# Global variables
#
logging.basicConfig(
    filename = 'pyradmon_log.log',
    filemode = 'a',
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt = '%d/%m/%Y %H:%M:%S %p',
    level = logging.INFO
);
gLogger = logging.getLogger('PyRadmon');

# =====================================================================================================================
# Type definitions and enums
#
@unique
class ProtocolType(Enum):
    """An enum class for the device protocol type

    Attributes
    ----------
    DEMO : int
        The Demo protocol (default 0)
    MYGEIGER : int
        The MyGeiger protocol (default 10)
    GMC : int
        The GMC protocol (default 11)
    NETIO : int
        The NetIO protocol (default 12)
    AUDIO : int
        The Audio protocol (default 20)
    """

    DEMO = 0;
    MYGEIGER = 10;
    GMC = 11;
    NETIO = 12;
    AUDIO = 20;

class SampleData():
    """Sample data object

    Methods
    -------
    __init__(cpm: int, timestamp: datetime)
        Initialize the object
    """

    def __init__(self, cpm: int, timestamp: datetime):
        """Initialize the object

        Parameters
        ----------
        cpm : int
            Counts per Minute value
        timestamp : datetime
            Measurement timestamp
        """

        self.cpm = cpm;
        self.timestamp = timestamp;

class Config():
    """A class representation of the `settings.cfg` file

    Attributes
    ----------
    CONFIGFILE : str
        The configuration file (default 'settings.cfg')
    logLevel : int
        The log level (default logging.INFO)
    user : str
        The username to use for RadMon (default 'not_set')
    password : str
        The password to use for RadMon (default 'not_set')
    protocol : ProtocolType
        The device protocol to use (default ProtocolType.DEMO)
    portName : str
        The serial port name (default 'not_set')
    portSpeed : int
        The serial port speed (default 2400)
    audioDevice : str
        The audio device name (default 'not_set')

    Methods
    -------
    fileExists()
        Checks if the `settings.cfg` file exists
    createDefault()
        Create a new file with the default configuration
    load()
        Load the configuration from the settings file
    """

    CONFIGFILE = 'settings.cfg';
    logLevel = logging.INFO;
    username = 'not_set';
    password = 'not_set';
    protocol = ProtocolType.DEMO;
    portName = 'not_set';
    portSpeed = 9600;
    audioDevice = 'not_set';
    audioThreshold = 0.05;

    def fileExists(self):
        """Checks if the `settings.cfg` file exists

        Returns
        -------
        bool
            False if the file does not exist
        """

        return os.path.exists(self.CONFIGFILE) and os.path.isfile(self.CONFIGFILE);

    def createDefault(self):
        """Create a new file with the default configuration

        This default configuration will be fully commented where needed.
        """

        print(MSG_NEW_CONFIG);
        gLogger.info(MSG_NEW_CONFIG);
       
        try:
            protocols = ['DEMO'];

            if PYSERIAL_SUPPORT:
                protocols.append('MYGEIGER');
                protocols.append('GMC');
                protocols.append('NETIO');
            # End if

            if SOUNDCARD_SUPPORT:
                protocols.append('AUDIO');
            # End if

            fileHandle = open(self.CONFIGFILE, 'w');
            fileHandle.write("// Parameter names are not case-sensitive\n");
            fileHandle.write("// Parameter values are case-sensitive\n");
            fileHandle.write("// Log levels: 10 = DEBUG, 20 = INFO, 30 = WARNING, 40 = ERROR, 50 = CRITICAL\n");
            fileHandle.write("log_level=%s\n" % (self.logLevel));
            fileHandle.write("// The Radmon username and password\n");
            fileHandle.write("username=%s\n" % (self.username));
            fileHandle.write("password=%s\n" % (self.password));
            fileHandle.write("// Protocols: %s\n" % (', '.join(protocols)));
            fileHandle.write("protocol=%s\n" % (self.protocol.name));

            if PYSERIAL_SUPPORT:
                fileHandle.write("// Port is usually /dev/ttyUSBx on Linux and COMx on Windows\n");
                fileHandle.write("serial_port=%s\n" % (self.portName));
                fileHandle.write("serial_speed=%s\n" % (self.portSpeed));
            # End if

            if SOUNDCARD_SUPPORT:
                fileHandle.write("// In case of audio, set the device ID here.\n");

                for dev in soundcard.all_microphones():
                    fileHandle.write("// ID: %s ; Name: %s\n" % (dev.id, dev.name));
                # End for

                fileHandle.write("audio_device=%s\n" % (self.audioDevice));
                fileHandle.write("audio_threshold=%s\n" % (self.audioThreshold));
            # End if

            print(
                "Please open the configuration file (`%s`) using your prefered text editor and update the settings.\n"
                % (self.CONFIGFILE)
            );
        except Exception as e:
            print(MSG_FMT_CONFIG_CREATE_FAIL % (str(e)));
            gLogger.exception(MSG_FMT_CONFIG_CREATE_FAIL, str(e));
        finally:
            time.sleep(0.1);
            fileHandle.close();
        # End try

    def load(self):
        """Load the configuration from the settings file

        The configuration file's contents should be compatible with this class.
        """

        fileHandle = None;

        try:
            fileHandle = open(self.CONFIGFILE, 'rt');

            for line in fileHandle:
                if line.startswith('//'):
                    continue;
                # End if

                params = line.split('=');

                if len(params) == 2:
                    parameter = params[0].strip().lower();
                    value = params[1].split('//')[0].strip();

                    if parameter == 'log_level':
                        self.logLevel = int(value);
                    elif parameter == 'username':
                        self.username = value;
                    elif parameter == 'password':
                        self.password = value;
                    elif parameter == 'protocol':
                        self.protocol = ProtocolType[value];
                    elif parameter == 'serial_port':
                        self.portName = value;
                    elif parameter == 'serial_speed':
                        self.portSpeed = int(value);
                    elif parameter == 'audio_device':
                        self.audioDevice = value;
                # End if
            # End for

            fileHandle.close();
        except Exception as e:
            print(MSG_FMT_CONFIG_READ_FAIL % (str(e)));
            gLogger.exception(MSG_FMT_CONFIG_READ_FAIL, str(e));

            if fileHandle != None:
                fileHandle.close();
            # End if

            sys.exit(1);
        # End try

class WebWorker():
    """Class for dealing with web requests

    Attributes
    ----------
    HOST : str
        The hostname of the server we need to communicate with
    PORT : int
        The TCP port to communicate with

    Methods
    -------
    __init__(cfg: Config)
        Initializer
    sendSample(sample: SampleData)
        Send the sample to Radmon
    """

    HOST = 'radmon.org';
    PORT = 443;

    def __init__(self, cfg: Config):
        self.username = cfg.username;
        self.password = cfg.password;

    def sendSample(self, sample: SampleData):
        if (self.username == '') or (self.password == ''):
            return;
        # End if

        print(MSG_FMT_SAS % (sample.cpm));
        gLogger.info(MSG_FMT_SAS, sample.cpm);

        try:
            conn = webClient.HTTPSConnection(self.HOST, self.PORT, timeout=60);
            conn.request(
                'GET',
                RADMON_URL_FMT % (
                    self.username,
                    self.password,
                    sample.timestamp.strftime('%Y-%m-%d%%20%H:%M:%S'),
                    sample.cpm
                ),
                headers={
                    'User-Agent': ('PyRadmon %s' % (__version__))
                }
            );
            res = conn.getresponse();
            data = res.read().decode('utf-8');
            gLogger.debug("Server response:\n%s", data);

            for line in data.replace('\r', '').split("\n"):
                print(line);

                if 'incorrect' in line.lower() :
                    print(MSG_INCORRECT_CREDENTIALS);
                    gLogger.warning(MSG_INCORRECT_CREDENTIALS);
                    sys.exit(1);
                # End if
            # End for
        except Exception as ex:
            print(MSG_FMT_WEB_ERROR % (str(ex)));
            gLogger.exception(MSG_FMT_WEB_ERROR, str(ex));
        # End try

class BaseDevice(threading.Thread):
    terminated = False;
    queueLocked = False;

    def __init__(self, deviceName: str, threadId: int, cfg: Config):
        threading.Thread.__init__(self);
        self.deviceName = deviceName;
        self.name = '%s_thread%s' % (deviceName, threadId);
        self.threadID = threadId;
        self.counter = threadId;
        self.webWorker = WebWorker(cfg);
        self.queue = deque();

    def run(self):
        print(MSG_FMT_DATA_STARTED % (self.name));
        gLogger.info(MSG_FMT_DATA_STARTED, self.name);

    def stop(self):
        self.terminated = True;
        self.queueLocked = False;

    def sendResult(self):
        while len(self.queue) <= 0: # Wait until we have data in the queue
            time.sleep(0.1);
            

        # Check if it's safe to process queue
        while self.queueLocked:
            gLogger.debug(MSG_QUEUE_LOCKED);
            time.sleep(0.01);
        # End while

        # Put lock so measuring process will not interfere with queue,
        # processing should be fast enought to not break data acquisition from geiger
        self.queueLocked = True;
        cpm = 0;

        # Now get sum of all CPM's
        for singleData in self.queue:
            cpm += singleData;

        cpm = int(float(cpm) / len(self.queue));
        self.queue.clear();
        self.queueLocked = False;
        self.webWorker.sendSample(SampleData(cpm, datetime.datetime.utcnow()));

    def getData(self):
        return;

class DemoDevice(BaseDevice):
    def __init__(self, threadId: int, cfg: Config):
        super().__init__('DemoDevice', threadId, cfg);

    def run(self):
        super().run();

        while not self.terminated:
            cpm = self.getData();

            while self.queueLocked:
                gLogger.debug(MSG_QUEUE_LOCKED);
                time.sleep(0.01);
            # End while

            self.queueLocked = True;
            self.queue.append(cpm);
            self.queueLocked = False;
            print(MSG_FMT_NEW_DATA % (cpm));
            gLogger.info(MSG_FMT_NEW_DATA, cpm);
        # End while

    def getData(self):
        for i in range(0, 50):
            time.sleep(0.1);

            if self.terminated:
                return;
            # End if
        # End for

        return random.randint(5, 40);

if PYSERIAL_SUPPORT:
    class SerialDevice(BaseDevice):
        serialPort = None;

        def __init__(self, deviceName: str, threadId: int, cfg: Config):
            super().__init__(deviceName, threadId, cfg);
            self.portName = cfg.portName;
            self.portSpeed = cfg.portSpeed;

        def run(self):
            super().run();

            try:
                self.serialPort = serial.Serial(self.portName, self.portSpeed, timeout = 1);
                self.serialPort.flushInput();
                self.initCommunication();

                while not self.terminated:
                    result = self.getData();

                    while self.queueLocked:
                        gLogger.debug(MSG_QUEUE_LOCKED);
                        time.sleep(0.01);
                    # End while

                    self.queueLocked = True;
                    self.queue.append(result);
                    self.queueLocked = False;
                # End while

                self.serialPort.close();
            except serial.SerialException as e:
                print(MSG_FMT_SERIAL_EXCEPTION % (str(e)));
                gLogger.exception(MSG_FMT_SERIAL_EXCEPTION, str(e));
                self.stop();
                time.sleep(1);
                sys.exit(1);
            # End try

        def initCommunication(self):
            return;

        def sendCommand(self, command: str):
            """Send a command to the serial port
            
            Parameters
            ----------
            command : str
                The command to send

            Returns
            -------
            str
                The result of the command
            """

            self.serialPort.flushInput();
            self.serialPort.write(command);
            time.sleep(0.5); # Assume that device responds within 0.5s
            response = '';

            while (self.serialPort.inWaiting() > 0) and (not self.terminated):
                response += self.serialPort.read();
            # End while

            return response;

    class MyGeigerDevice(SerialDevice):
        def __init__(self, threadId: int, cfg: Config):
            super().__init__('MyGeigerDevice', threadId, cfg);

        def run(self):
            super().run();

    class GMCDevice(SerialDevice):
        def __init__(self, threadId: int, cfg: Config):
            super().__init__('GMCDevice', threadId, cfg);

        def run(self):
            super().run();

    class NetIODevice(SerialDevice):
        def __init__(self, threadId: int, cfg: Config):
            super().__init__('NetIODevice', threadId, cfg);

        def run(self):
            super().run();
# End if

if SOUNDCARD_SUPPORT:
    class AudioDevice(BaseDevice):
        noisyCount = 0;
        noisyBlock = False;
        loopCounter = 0;
        sampleRate = 44100;
        blocksPerSecond = 100;
        frameCount = int((sampleRate / blocksPerSecond) * 1);

        def __init__(self, threadId: int, cfg: Config):
            super().__init__('AudioDevice', threadId, cfg);
            self.device = soundcard.get_microphone(cfg.audioDevice);
            self.threshold = cfg.audioThreshold;

        def run(self):
            super().run();

            with self.device.recorder(self.sampleRate) as mic:
                while not self.terminated:
                    data = mic.record(self.frameCount);
                    rms = sqrt(mean(square(data)));

                    if rms >= self.threshold:
                        if not self.noisyBlock:
                            self.noisyBlock = True;
                            gLogger.debug('Noisy block start');

                            while self.queueLocked:
                                gLogger.debug(MSG_QUEUE_LOCKED);
                                time.sleep(0.01);
                            # End while

                            self.queueLocked = True;
                            self.noisyCount += 1;
                            self.queueLocked = False;
                        # End if
                    elif self.noisyBlock:
                        self.noisyBlock = False;
                        gLogger.debug('Noisy block end');
                    # End if
                # End while
            # End with

        def sendResult(self):
            while self.queueLocked:
                gLogger.debug(MSG_QUEUE_LOCKED);
                time.sleep(0.01);
            # End while

            self.queueLocked = True;
            cpm = self.noisyCount;
            self.noisyCount = 0;
            self.queueLocked = False;
            self.webWorker.sendSample(SampleData(int(cpm * 2), datetime.datetime.utcnow()));
# End if

class PyRadmon():
    """Main class

    Typical main class.
    - Create the config object
    - Check if the config file exists, if not create it
    - Spin up threads to do work
    """

    threads = [];
    threadCounter = 0;
    terminated = False;

    def __init__(self):
        self.cfg = Config();

    def run(self):
        if not self.cfg.fileExists():
            self.cfg.createDefault();
            sys.exit(0);
        # End if

        self.cfg.load();
        gLogger.setLevel(self.cfg.logLevel);

        # Create geiger communication object
        if (self.cfg.protocol == ProtocolType.MYGEIGER) and PYSERIAL_SUPPORT:
            device = MyGeigerDevice(++self.threadCounter, self.cfg);
        elif (self.cfg.protocol == ProtocolType.GMC) and PYSERIAL_SUPPORT:
            device = GMCDevice(++self.threadCounter, self.cfg);
        elif (self.cfg.protocol == ProtocolType.NETIO) and PYSERIAL_SUPPORT:
            device = NetIODevice(++self.threadCounter, self.cfg);
        elif (self.cfg.protocol == ProtocolType.AUDIO) and SOUNDCARD_SUPPORT:
            device = AudioDevice(++self.threadCounter, self.cfg);
        else:
            device = DemoDevice(++self.threadCounter, self.cfg);

        gLogger.debug(MSG_FMT_PROTOCOL, device.deviceName);
        device.start();
        self.threads.append(device);

        while True:
            for i in range(0, 299):
                time.sleep(0.1);

                if self.terminated:
                    break;
                # End if
            # End for

            if not self.terminated:
                for thread in self.threads:
                    thread.sendResult();
                # End for
            # End if
        # End while

    def stop(self):
        self.terminated = True;
        print(MSG_WAIT_FOR_THREAD);
        gLogger.warning(MSG_WAIT_FOR_THREAD);
        time.sleep(1); # Give everything some time to shut down

        for thread in self.threads:
            print(MSG_FMT_STOPPING_THREAD % (thread.getName()));
            gLogger.info(MSG_FMT_STOPPING_THREAD, thread.getName());
            thread.stop();
            time.sleep(1);
            thread.join();
        # End for

        print(MSG_SHUTDOWN);
        gLogger.info(MSG_SHUTDOWN);

# =====================================================================================================================
# Entry point
#
def main():
    """Entry point

    Just creates the main application object and starts running the app
    """
    
    app = PyRadmon();

    try:
        app.run();
    except KeyboardInterrupt as e:
        print(MSG_CTRL_C_EXIT);
        gLogger.info(MSG_CTRL_C_EXIT);
    except SystemExit as e:
        if e.code() != 0:
            print(MSG_FMT_SYS_EXIT % (MSG_SYS_EXIT, str(e)));
            gLogger.warning(MSG_FMT_SYS_EXIT, MSG_SYS_EXIT, str(e));
        else:
            print(MSG_SYS_EXIT);
            gLogger.info(MSG_SYS_EXIT);
    except Exception as e:
        print(MSG_FMT_EXCEPTION % (str(e)));
        gLogger.error(MSG_FMT_EXCEPTION, str(e));
    # End try

    app.stop();
    gLogger.info(MSG_END_OF_LOG);
    logging.shutdown();

if __name__ == '__main__':
    main();
# End if
