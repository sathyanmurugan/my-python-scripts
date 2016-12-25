# -*- coding: utf-8 -*-
# Environment: Python 2.7
# Author: Sathyan Murugan


import win_inet_pton
import socks
import socket
import requests

def connect_to_tor():
	socks.setdefaultproxy(proxy_type=socks.PROXY_TYPE_SOCKS5, addr="127.0.0.1", port=9050)
	socket.socket = socks.socksocket
	print ( "Connected to Tor with IP - " + requests.get("http://icanhazip.com").text)


def refresh_ip():

	socks.setdefaultproxy()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(("127.0.0.1", 9051))
	s.send("AUTHENTICATE\r\n")
	s.send("SIGNAL NEWNYM\r\n")
	s.close()
	connect_to_tor()

