"""
This is a wrapper for the Python library beatbox
beatbox: Makes the salesforce.com SOAP API easily accessible
Cloned from -> Github: https://github.com/superfell/Beatbox

IMPORTANT: The beatbox package used here is not the same as the one available with pip on PyPI,
which is an older version and is only compatible with Python 2.7 and lower
"""

import salesforce.beatbox as beatbox
from math import ceil
from datetime import datetime,timedelta
import logging
import pandas as pd
from bs4 import BeautifulSoup


__version__ = "0.2"
__author__ = "Sathyan Murugan"
__credits__ = "Mad shouts to the sforce possie, Superfell, Hynecker and other crazy people"


class Salesforce:
	
	def __init__(self,sf_user,sf_pw):

		self.sf = beatbox._tPartnerNS
		self.svc = beatbox.Client()
		beatbox.gzipRequest = False
		loginResult = self.svc.login(sf_user,sf_pw)
		self.userId = str(loginResult[0][self.sf.userInfo][self.sf.userId])
		self.logger = logging.getLogger(__name__ + '.Salesforce')


	def _get_fields(self,query_string):
		'''
		Extracts the fields from the query
		'''
		alpha = "SELECT"
		bravo = "FROM "
		startpos = query_string.upper().find(alpha) + len(alpha)
		endpos = query_string.upper().find(bravo, startpos)
		dirty_fields = query_string[startpos:endpos].replace(' ','').split(',')
		fields = [field.strip() for field in dirty_fields]

		return fields


	def query(self,query_string):


		qr = self.svc.query(query_string)[0]
		results = qr[self.sf.records:]
		result_size = str(qr[self.sf.size])

		while str(qr[self.sf.done]) == 'false':
			qr = self.svc.queryMore(str(qr[self.sf.queryLocator]))[0]
			results.extend(qr[self.sf.records:])

		#Extract fields from query string
		fields = self._get_fields(query_string)

		data_list = []
		for result in results:
			data_dict = {}
			for val,field in zip(result[2:],fields):
				data_dict[field] = str(val)
			data_list.append(data_dict)

		return data_list


	def query_all(self,query_string):
		'''
		Also queries deleted records
		'''

		qr = self.svc.queryAll(query_string)[0]
		results = qr[self.sf.records:]
		result_size = str(qr[self.sf.size])

		while str(qr[self.sf.done]) == 'false':
			qr = self.svc.queryMore(str(qr[self.sf.queryLocator]))[0]
			results.extend(qr[self.sf.records:])

		#Extract fields from query string
		fields = self._get_fields(query_string)

		data_list = []
		for result in results:
			data_dict = {}
			for val,field in zip(result[2:],fields):
				data_dict[field] = str(val)
			data_list.append(data_dict)

		return data_list


	def _get_list_dicts(self,data_to_sf):
		'''
		Checks type of input and converts to list of dicts if necessary
		'''

		if isinstance(data_to_sf, pd.DataFrame):
			#NaN to None
			data_to_sf = data_to_sf.where((pd.notnull(data_to_sf)), None)
			list_dicts = data_to_sf.to_dict('records')
		
		elif isinstance(data_to_sf,list) and isinstance(data_to_sf[0],dict):
			list_dicts = data_to_sf

		elif isinstance(data_to_sf,str):
			df = pd.read_csv(data_to_sf,encoding='latin1')
			df = df.where((pd.notnull(df)), None)
			list_dicts = df.to_dict('records')

		else:
			raise RuntimeError("""
				Incorrect input type for this operation. Please pass one of the following 
				- list of dictionaries
				- Pandas DataFrame
				- Path to a CSV file
				""")

		return list_dicts


	def _prep_data(self,list_dicts,batch_size):

		#Convert data to str if not null
		for dic in list_dicts:
			for key in dic:
				if dic[key] != None:
					dic[key] = str(dic[key]) 

		#Calculate the number of batches to upload
		num_batches = ceil(len(list_dicts)/batch_size)
		
		#Break the list of dicts into batches 
		batches = [[] for x in range(num_batches)]
		for index, item in enumerate(list_dicts):
			batches[index % num_batches].append(item)

		return batches


	def _parse_xml_result(self,result,update_ids=None):
		'''
		Parse XML response using BeautifulSoup  
		'''

		soup = BeautifulSoup(result,'lxml')
		results = soup.findAll('result')
		parsed_results = []

		if update_ids:

			for result,update_id in zip(results,update_ids):
				result_dict = {}

				for elem in ['success','id','fields','message','statuscode']:
					if result.find(elem):
						result_dict[elem] = result.find(elem).get_text()
					else:
						result_dict[elem] = None

				if result_dict['id'] is None or result_dict['id'] == '':
					result_dict['id'] = update_id

				parsed_results.append(result_dict)
		
		else:
			
			for result in results:
				result_dict = {}

				for elem in ['success','id','fields','message','statuscode']:
					if result.find(elem):
						result_dict[elem] = result.find(elem).get_text()
					else:
						result_dict[elem] = None

				parsed_results.append(result_dict)

		return parsed_results


	def create(self,data_to_sf,batch_size=200):
		'''
		
		data_to_sf - can be one of the following:
				- list of dictionaries
				- a pandas dataframe
				- path to csv

		Always add a column 'type' = name of the sforce object being acted upon
		'''

		list_dicts = self._get_list_dicts(data_to_sf)

		batches = self._prep_data(list_dicts,batch_size)
		counter = 0
		results = []

		for batch in batches:
			counter+=1
			self.logger.info ('Inserting batch %d of %d' % (counter,len(batches)))
			result = self.svc.create(batch)
			parsed_result = self._parse_xml_result(result[1])
			results.extend(parsed_result)

		return results		


	def update(self,data_to_sf,batch_size=200):
		'''
		data_to_sf - can be one of the following:
				- list of dictionaries
				- a pandas dataframe
				- path to csv

		Always add a column 'type' = name of the sforce object being acted upon
		'''

		list_dicts = self._get_list_dicts(data_to_sf)
		batches = self._prep_data(list_dicts,batch_size)
		counter = 0
		results = []

		for batch in batches:
			update_ids = [dic['Id'] for dic in batch]
			counter+=1
			self.logger.info ('Updating batch %d of %d' % (counter,len(batches)))
			result = self.svc.update(batch)
			parsed_result = self._parse_xml_result(result[1],update_ids)
			results.extend(parsed_result)

		return results


	def delete(self,list_ids):
		'''
		Input is a list, not a list of dicts
		List should contain only the Id of the record being deleted, no type is required
		'''

		counter = 0
		results = []

		for record_id in list_ids:
			counter+=1
			self.logger.info ('Deleting record %d of %d' % (counter,len(list_ids)))
			result = self.svc.delete(record_id)
			parsed_result = self._parse_xml_result(result[1])
			results.append(parsed_result)

		return results