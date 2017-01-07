# -*- coding: utf-8 -*-
# Environment: Python 2.7
# Author: Sathyan Murugan

"""
This file contains methods to connect to Tor.

IMPORTANT ---> Before executing this file:

1. Download Tor Expert Bundle from: https://www.torproject.org/download/download
2. Extract contents
3. Open up a command prompt and execute the following command "path/to/tor/executable/file --ControlPort 9051"
4. Leave this shell open for the entire duration of the Python scipt execution. Closing the shell will terminate the connection to Tor.

"""

import win_inet_pton
import socks
import socket
import requests
import time

def connect_to_tor():
	socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
	socket.socket = socks.socksocket


def refresh_ip():

	socks.setdefaultproxy()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	#Connect through controlport 9051 to send commands
	s.connect(("127.0.0.1", 9051))
	s.send("AUTHENTICATE\r\n")
	s.send("SIGNAL NEWNYM\r\n")
	s.close()
	connect_to_tor()


if __name__ == '__main__':

	#Connect to tor
	connect_to_tor()
	print ("Connected to Tor with IP - " + requests.get("http://icanhazip.com").text)

	#Wait a bit before refreshing the IP
	time.sleep(5)

	#Refresh IP (beware of rate limiting by tor if this is done too frequently)
	refresh_ip()
	print ("Refreshed IP. New IP is - " + requests.get("http://icanhazip.com").text)