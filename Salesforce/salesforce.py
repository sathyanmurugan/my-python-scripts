# -*- coding: utf-8 -*-
# Environment: Python 2.7
# Author: Sathyan Murugan

"""
This file contains methods to connect to the Salesforce API and 
is based on the Salesforce-Python wrapper "beatbox" by Superfell.

Github link for Beatbox: https://github.com/superfell/Beatbox

"""


import beatbox
import math

class Salesforce:

	def __init__(self, sf_username, sf_password_token):
		self.sf = beatbox.PythonClient()
		self.sf.login(sf_username,sf_password_token)


	def prep_data(self,list_dicts,batch_size):

		#Convert data to str if not null
		for dic in list_dicts:
			for key in dic:
				if dic[key] != None:
					dic[key] = str(dic[key]) 

		#Calculate the number of batches to upload
		num_batches = int(math.ceil(len(list_dicts)/batch_size))
		
		#Break the list of dicts into batches 
		batches = [[] for x in range(num_batches)]
		for index, item in enumerate(list_dicts):
			batches[index % num_batches].append(item)

		return batches


	def insert(self,batches):

		results = []
		counter = 0

		#Upload in batches
		for batch in batches:
			counter = counter + 1
			print ('processing batch %d of %d' % (counter,len(batches)))
			batch_result = self.sf.create(batch)
			results.extend(batch_result)

		return results

	
	def update(self,batches,update_ids):

		results = []
		counter = 0

		#Upload in batches
		for batch in batches:
			counter = counter + 1
			print ('processing batch %d of %d' % (counter,len(batches)))
			batch_result = self.sf.update(batch)
			results.extend(batch_result)

		#Add Id to the result (errors dont contain the update Id)
		for Id, result in zip(update_ids,results):
			result['id'] = Id

		return results
	


	def upsert(self,batches,upsert_field,upsert_ids):

		results = []
		counter = 0

		#Upload in batches
		for batch in batches:
			counter = counter + 1
			print ('processing batch %d of %d' % (counter,len(batches)))
			batch_result = self.sf.upsert(upsert_field,batch)
			results.extend(batch_result)

		#Add Id to the result (errors dont contain the upsert Id)
		for Id, result in zip(upsert_ids,results):
			result['id'] = Id

		return results


	def query(self,sf_query):

		query_result = sf.query(sf_query)
		records = query_result["records"]
		total_records = query_result['size']
		query_locator = query_result['queryLocator']
		query_counter = 1
		query_batches = int(math.ceil(total_records/500.0))

		while query_result['done'] is False and len(records) < total_records:

			query_counter = query_counter + 1
			print ("extracting batch %d of %d" % (query_counter,query_batches))
			query_result = sf.queryMore(query_locator)
			query_locator = query_result['queryLocator']
			records = records + query_result['records']

		return records


	def delete(self,batches):

		#Batches should contain only the Id of the record being deleted

		results = []
		counter = 0

		#Upload in batches
		for batch in batches:
			counter = counter + 1
			print ('processing batch %d of %d' % (counter,len(batches)))
			batch_result = self.sf.delete(batch)
			results.extend(batch_result)

		return results


	def convert_lead(self,batches):

		results = []
		counter = 0

		#Upload in batches
		for batch in batches:
			counter = counter + 1
			print ('processing batch %d of %d' % (counter,len(batches)))
			batch_result = self.sf.convertLead(batch)
			results.extend(batch_result)

		return results