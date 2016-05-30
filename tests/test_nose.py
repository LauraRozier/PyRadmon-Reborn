'''
Test PyRadmon_No_Audio.PyRadmon with nose 
To run tests : nosetests    test_nose.py
Verobse (-v) : nosetests -v test_nose.py
'''

from PyRadmon_No_Audio.PyRadmon import config

# create and read configuration data
cfg = config()
cfg.readConfig()

def test_cfg_user():
    assert cfg.user == "test_user"

def test_cfg_password():
    assert cfg.password == "test_password"

def test_cfg_portName():
    assert cfg.portName == "/dev/ttyUSB0"

def test_cfg_portSpeed():
    assert cfg.portSpeed == 2400

def test_cfg_protocol():
    assert cfg.protocol == config.DEMO
