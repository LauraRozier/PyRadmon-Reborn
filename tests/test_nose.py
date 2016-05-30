'''
Test PyRadmon_No_Audio.PyRadmon with nose 
To run tests : nosetests    test_nose.py
Verobse (-v) : nosetests -v test_nose.py
'''
from nose import with_setup # optional
import PyRadmon_No_Audio.PyRadmon as PyRadmon

def setup_module(module):
    print("")
    print("Starting tests for PyRadmon")

def teardown_module(module):
    print("")
    print("Done running tests for PyRadmon")

# create and read configuration data
cfg = PyRadmon.config()
cfg.readConfig()

class TestUM:
	
    def setup(self):
        print("")
        print("----------------------------------------------")
        print("Starting test ")

    def teardown(self):
        print("Done running test ")
        print("----------------------------------------------")

    def test_cfg_user(self):
        print("Testing to determine if the default value of cfg.user equals test_user")
        assert cfg.user == "test_user"

    def test_cfg_password(self):
        print("Testing to determine if the default value of cfg.password equals test_password")
        assert cfg.password == "test_password"

    def test_cfg_portName(self):
        print("Testing to determine if the default value of cfg.portName equals /dev/ttyUSB0")
        assert cfg.portName == "/dev/ttyUSB0"

    def test_cfg_portSpeed(self):
        print("Testing to determine if the default value of cfg.portSpeed equals 2400")
        assert cfg.portSpeed == 2400

    def test_cfg_protocol(self):
        print("Testing to determine if the default value of cfg.protocol equals PyRadmon.config.DEMO")
        assert cfg.protocol == PyRadmon.config.DEMO
