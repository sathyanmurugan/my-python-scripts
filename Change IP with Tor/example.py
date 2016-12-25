# -*- coding: utf-8 -*-
# Environment: Python 2.7
# Author: Sathyan Murugan

"""
This file contains methods to connect to Tor 

Before executing this file:
1. Download Tor Expert Bundle from: https://www.torproject.org/download/download
2. Extract contents

"""
import tor
import os

#Specify the path to the executable Tor file in the extracted bundle
path_to_tor_exe = r'C:\Users\smurugan\Documents\"Python Scripts"\tor-win32-0.2.7.6\Tor\tor.exe'

os.system(path_to_tor_exe + ' --ControlPort 9051')

#Connect to tor
tor.connect_to_tor

#Refresh IP if necessary (beware of rate limiting by tor if this is done too frequently)
tor.refresh_ip

