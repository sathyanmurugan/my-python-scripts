#!/usr/bin/env python3
#
# Author: Sathyan Murugan (sathyan.murugan@blacklane.com)
# Year:   2017

"""
This file contains methods to connect to Holiday API (a RESTful service for obtaining holiday data)
and return holidays for a given country, month and year.

API key is required

Documentation: https://holidayapi.com
"""

import requests
import json
import urllib.parse


class HolidayAPI():

	def __init__(self,holiday_api_key):

		self.key = holiday_api_key
		self.api_endpoint = 'https://holidayapi.com/v1/holidays'


	def get_holidays(self,country_code,month,year):
		'''
		For country codes -> https://holidayapi.com
		'''
		payload = {
		"key": self.key,
		"country":country_code,
		'year':year,
		'month':month
		}

		r = requests.get(self.api_endpoint,params=urllib.parse.urlencode(payload))
		response = r.json()
		
		return response
