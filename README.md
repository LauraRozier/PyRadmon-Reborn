# PyRadmon-Reborn
[![Python Versions](https://img.shields.io/badge/Python-2.7-brightgreen.svg)](https://github.com/thibmo/PyRadmon-Reborn) [![Build Status](https://travis-ci.org/thibmo/PyRadmon-Reborn.svg?branch=master)](https://travis-ci.org/thibmo/PyRadmon-Reborn)  
[//]: # (Title and short description)
PyRadmon, a Python radiation monitoring util to use on both Linux and Windows.

### Installation
[//]: # (Installation requirements with links)
The first thing you should know is whether you would like to use one, or two counters.  
In the case of a single counter you should download PyRadmon, in the case of two counters use MultiPyRadmon  
**Always use the right file for the right amount of counters!**

#### Windows
##### Preparing
To use PyRadmon Reborn on your Windows machine you would first have to follow the following steps.
- Install Python
  - Download [Python 2.7.x for Windows][WinPython].
  - Install Python 2.7.x with it's default settings, making sure to read well,  
    the installer must create the edit to the system variables.
- Install PIP (If it is not yet installed)
  - Test if PIP is installed.  
    ```python -m pip list```
  - If Python gave an error, you should [install PIP][PIPHelp].
- Install PySerial
  - Install PySerial for Python 2.7 with it's default settings.  
    ```python -m pip install pyserial```
- Install PyAudio
  - Install PyAudio for Python 2.7 with it's default settings.  
    ```python -m pip install pyaudio```
- Download (Multi)PyRadmon.py
  - [Download][PyRadmonDownload] the preferred version.
  - Put the file to the preferred location.

#### \*bian/\*buntu
##### Preparing
To use PyRadmon Reborn on your Linux machine you would first have to follow the following steps.
- Install using these commands for python, PySerial and PyAudio.  
  (If in GUI mode, first open the Terminal, **NOT THE ROOT TERMINAL**.)
  - cd ~
  - sudo apt-get install python-dev
  - sudo apt-get install python-serial
  - su
  - [Type your password, if required.]
  - adduser <yourusername> dialout
  - reboot
  - [Log back in to the user you used before.]
  - cd ~
  - sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev
  - sudo apt-get install git
  - sudo git clone [http://people.csail.mit.edu/hubert/git/pyaudio.git][GitPyAudio]
  - cd pyaudio
  - sudo python setup.py install
- Download (Multi)PyRadmon.py
  - [Download][PyRadmonDownload] the preferred version.
    - For MultiPyRadmon  
      ```wget 'https://github.com/thibmo/PyRadmon-Reborn/releases/download/v1.2.0/MultiPyRadmon[.-.No.Audio].zip'```
    - For PyRadmon  
      ```wget 'https://github.com/thibmo/PyRadmon-Reborn/releases/download/v1.2.0/PyRadmon[.-.No.Audio].zip'```
  - Unpack the tarball to the preferred location.  
    ```tar zxvf (Multi)PyRadmon.tar.gz -C ~/PyRadmon```

### Running PyRadmon Reborn for the first time
#### Windows
- Run (Multi)PyRadmon.py once.
  - Open command prompt
    - Click on Start
    - Type "cmd" in the search bar.
    - Right click CMD.exe and left click "Run as Administrator"
    - If you are asked for a confirmation, select "Yes" or "Ok"
  - Change the directory to where you have downloaded (Multi)PyRadmon.py  
    Eg: cd C:\Users\<Username>\Downloads
  - Run (Multi)PyRadmon.py once to create the config file.
    - ```python ./(Multi)PyRadmon.py``` *
    - Close the command prompt.
- Edit the config.txt file, this will be created in the same directory where you stored your (Multi)PyRadmon.py
- Run (Multi)PyRadmon again, it will now start monitoring/uploading to Radmon.org using the configured settings.
  - Open command prompt
    - Click on Start
    - Type "cmd" in the search bar.
    - Right click CMD.exe and left click "Run as Administrator"
    - If you are asked for a confirmation, select "Yes" or "Ok"
  - Change the directory to where you have downloaded (Multi)PyRadmon.py  
    Eg: cd C:\Users\<Username>\Downloads
  - Run (Multi)PyRadmon.py.
    - ```python ./(Multi)PyRadmon.py``` *

\* = Might this give you an error, follow these steps: Python help on Windows

#### \*bian/\*buntu
- Run (Multi)PyRadmon.py once.
  - In the command line type:
    - ```cd ../Location/To/The/File```
    - ```python ./(Multi)PyRadmon.py```
  - In the GUI:
    - Open the Terminal and type:
      - ```cd ../Location/To/The/File```
      - ```python ./(Multi)PyRadmon.py```
- Edit the config.txt file, this will be created in the same directory where you stored your (Multi)PyRadmon.py
  - ```nano config.txt```
  - In nano you can exit with saving by pressing [Ctrl] and [X] simultaneously, then pressing [Y] to confirm.
- Run (Multi)PyRadmon again, it will now start monitoring/uploading to Radmon.org using the configured settings.
  - ```python ./(Multi)PyRadmon.py```

### Updating PyRadmon Reborn
#### Windows
- Stop the program
  - Press [Ctrl] and [C] simultaneously.
  - Close the command prompt
- Delete the old files and folder
- Download (Multi)PyRadmon.py (Multi)PyRadmon.zip
  - Download the preferred version in .zip format.
  - Unpack the file to the preferred location.
- Run (Multi)PyRadmon.py once.
  - Open command prompt
    - Click on Start
    - Type "cmd" in the search bar.
    - Right click CMD.exe and left click "Run as Administrator"
    - If you are asked for a confirmation, select "Yes" or "Ok"
  - Change the directory to where you have downloaded (Multi)PyRadmon.py  
    Eg: cd C:\Users\<Username>\Downloads
  - Run (Multi)PyRadmon.py once to create the config file.
    - ```python ./(Multi)PyRadmon.py``` *
    - Close the command prompt.
- Edit the config.txt file, this will be created in the same directory where you stored your (Multi)PyRadmon.py
- Run (Multi)PyRadmon again, it will now start monitoring/uploading to Radmon.org using the configured settings.
  - Open command prompt
    - Click on Start
    - Type "cmd" in the search bar.
    - Right click CMD.exe and left click "Run as Administrator"
    - If you are asked for a confirmation, select "Yes" or "Ok"
  - Change the directory to where you have downloaded (Multi)PyRadmon.py  
    Eg: cd C:\Users\<Username>\Downloads
  - Run (Multi)PyRadmon.py.
    - ```python ./(Multi)PyRadmon.py``` *

\* = Might this give you an error, follow these steps: Python help on Windows

#### \*bian/\*buntu
- Stop the program
  - Press [Ctrl] and [C] simultaneously.
- Delete the old files and folder
  - ```cd ~```
  - ```rm -rf PyRadmon```
- Download (Multi)PyRadmon.py (If in GUI mode, first open the Terminal, NOT THE ROOT TERMINAL.)
  - Download the preferred version in .tar.gz format.
    - For MultiPyRadmon
      - ```wget 'https://github.com/thibmo/PyRadmon-Reborn/releases/download/v1.2.0/MultiPyRadmon[.-.No.Audio].zip'```
    - For PyRadmon
      - ```wget 'https://github.com/thibmo/PyRadmon-Reborn/releases/download/v1.2.0/PyRadmon[.-.No.Audio].zip'```
- Unpack the tarball to the preferred location.
  - ```tar zxvf (Multi)PyRadmon.tar.gz -C ~/PyRadmon```
- Run (Multi)PyRadmon.py once.
  - ```cd ~/PyRadmon```
  - ```python ./(Multi)PyRadmon.py```
- Edit the config.txt file, this will be created in the same directory where you stored your (Multi)PyRadmon.py
  - ```nano config.txt```
  - In nano you can exit with saving by pressing [Ctrl] and [X] simultaneously, then pressing [Y] to confirm.
- Run (Multi)PyRadmon again, it will now start monitoring/uploading to Radmon.org using the configured settings.
  - ```python ./(Multi)PyRadmon.py```

### What script to use?
[//]: # (Some explainatory text about the different scripts)
It all depends on what your end-goal is.  
Below this text you will find a small guide to finding the script you will need.
- If you are not sure, or you have an audio counter, and you only have one device, then use "PyRadmon".
- If you don't need audio support and you only have one device, then use "PyRadmon - No Audio".
- If you are not sure, or you have an audio counter, and you have two devices, then use "MultiPyRadmon".
- If you don't need audio support and you have two devices, then use "MultiPyRadmon - No Audio".

[//]: # (Features and misc)
### Features
- This project is open for requests
- Audio meter support through "taps"
- UART-TTL USB module support
- DIY-kit support, for new kits I am willing to add special methods to process their data
- Reports CPM data from a Geiger counter to RadMon.org or any that support the format
- Supports MyGeiger counters (serial)
- Supports NetIO counters (serial)
- Supports GQElectronics GMC counters (serial)
- Supports two equal or different Geiger counters at the same time through multi-threading

[//]: # (Add links below this line)
  [WinPython]: <https://www.python.org/downloads/windows>
  [PIPHelp]: <http://pip.readthedocs.io/en/stable/installing>
  [GitPyAudio]: <http://people.csail.mit.edu/hubert/git/pyaudio.git>
  [PyRadmonDownload]: <https://github.com/thibmo/PyRadmon-Reborn/releases>
