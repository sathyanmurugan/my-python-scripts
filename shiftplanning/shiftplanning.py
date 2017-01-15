#!/usr/bin/env python3
#
# Author: Sathyan Murugan
# Year:   2016

"""
This file contains methods to connect to ShiftPlanning

Documentation: https://www.shiftplanning.com/api/

"""

import json
import urllib.parse
from urllib.request import urlopen
import datetime
import requests


class ShiftPlanning():

	def __init__(self,sp_api_key,sp_username,sp_password):
		
		self.key = sp_api_key
		self.username = sp_username
		self.password = sp_password
		self.api_endpoint = "https://www.shiftplanning.com/api/"
		self.token = None

		params = {"module": "staff.login",
				  "method": "GET",
				  "username": self.username,
				  "password": self.password}

		raw_data = urllib.parse.urlencode([('data', json.dumps({'key':self.key,'request':params}))])
		data = raw_data.encode('utf8')
		req = urllib.request.Request(self.api_endpoint, headers={'accept-charset':'UTF-8'})
		reader = urllib.request.urlopen(req, data)
		response = reader.read()
		response = json.loads(response.decode('utf-8'))
		self.token = response['token']


	def make_api_call(self,params):

		raw_data = urllib.parse.urlencode([('data', json.dumps({'token':self.token,'request':params}))])
		data = raw_data.encode('utf8')
		req = urllib.request.Request(self.api_endpoint, headers={'accept-charset':'UTF-8'})
		reader = urllib.request.urlopen(req, data)
		response = reader.read()
		response = json.loads(response.decode('utf-8'))

		return response


	def get_users(self):

		params = {"module": "staff.employees",
				  "method": "GET"}

		response = self.make_api_call(params)
		elements = response['data']

		return elements


	def get_schedules(self):

		params = {"module": "schedule.schedules",
				  "method": "GET"}

		response = self.make_api_call(params)
		elements = response['data']	

		return elements


	def get_report_schedule(self,start_date,end_date,report_type='crib_sheet'):

		params = {"module": "reports.schedule",
				  "method": "GET",
				  "start_date":start_date,
				  "end_date":end_date,
				  "type":report_type}

		response = self.make_api_call(params)
		elements = response['data']

		return elements

	
	def get_report_payroll(self,start_date,end_date,report_type='confirmedhours'):

		params = {"module": "payroll.report",
				  "method": "GET",
				  "start_date":start_date,
				  "end_date":end_date,
				  "type":report_type}

		response = self.make_api_call(params)
		raw_elements = response['data']

		elements = []

		for raw_k in raw_elements:
			if raw_k != 'split_rate':
				elements.append(raw_elements[raw_k])

		for k in elements:
			k['overtime'] = k['hours']['d_overtime']
			k['schedule'] = k['hours']['position']['name']
			k['regular'] = k['hours']['regular']
			k['special'] = k['hours']['special']
			k['total'] = k['hours']['total']

			start_day = k['date']['day']
			start_month = k['date']['month']
			start_year = k['date']['year']
			k['start_date'] = datetime.datetime(start_year,start_month,start_day).strftime('%Y-%m-%d')
			k['start_timestamp'] = k['start_date'] + ' ' + k['start_time']

			end_day = k['out_date']['day']
			end_month = k['out_date']['month']
			end_year = k['out_date']['year']
			k['end_date'] = datetime.datetime(end_year,end_month,end_day).strftime('%Y-%m-%d')
			k['end_timestamp'] = k['end_date'] + ' ' + k['end_time']

		return elements

