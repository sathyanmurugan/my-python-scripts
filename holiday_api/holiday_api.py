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