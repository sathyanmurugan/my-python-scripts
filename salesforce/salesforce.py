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


__version__ = "0.2"
__author__ = "Sathyan Murugan"
__credits__ = "Mad shouts to the sforce possie, Superfell, Hynecker and other crazy people"


class Salesforce:
	
	def __init__(self,sf_user,sf_pw):

		self.sf = beatbox._tPartnerNS
		self.svc = beatbox.Client()
		beatbox.gzipRequest = False
		loginResult = self.svc.login(sf_user,sf_pw)
		self.userId = str(loginResult[self.sf.userInfo][self.sf.userId])
		self.logger = logging.getLogger(__name__ + '.Salesforce')


	def _get_fields(self,query_string):
		'''
		Extracts the fields from the query
		'''
		alpha = "SELECT"
		bravo = "FROM"
		startpos = query_string.upper().find(alpha) + len(alpha)
		endpos = query_string.upper().find(bravo, startpos)
		dirty_fields = query_string[startpos:endpos].replace(' ','').split(',')
		fields = [field.strip() for field in dirty_fields]

		return fields


	def query(self,query_string):


		qr = self.svc.query(query_string)
		results = qr[self.sf.records:]
		result_size = str(qr[self.sf.size])

		while str(qr[self.sf.done]) == 'false':
			qr = self.svc.queryMore(str(qr[self.sf.queryLocator]))
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

	def _get_updated(self,field,sobjects,start_time,end_time):
		'''
		Get list of records updated between start_time and end_time by current user
		'''

		updated_records = []

		for sobject in sobjects:
			query_result = self.query("""
				SELECT {0}
				FROM {1} 
				WHERE LastModifiedDate>={2}
				AND LastModifiedDate<={3} 
				AND LastModifiedById ='{4}'
				""".format(
					field,
					sobject,
					start_time,
					end_time,
					self.userId
					))

			Ids = [dic[field] for dic in query_result]
			updated_records.extend(Ids)

		return updated_records


	def create(self,list_dicts,batch_size=200):
		'''
		Returns a dict of created Ids and number of failures
		'''

		#sforce Objects being updated
		sobjects = list(set([dic['type'] for dic in list_dicts]))

		batches = self._prep_data(list_dicts,batch_size)
		counter = 0

		#Salesforce time seems to be 15 seconds slower than UTC
		start_time = (datetime.utcnow() - timedelta(seconds=20)).strftime('%Y-%m-%dT%H:%M:%SZ')
		for batch in batches:
			counter+=1
			self.logger.info ('Inserting batch %d of %d' % (counter,len(batches)))
			batch_result = self.svc.create(batch)

		end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

		records_created = self._get_updated('Id',sobjects,start_time,end_time)

		data_dict = {
		'success':records_created,
		'errors': len(list_dicts) - len(records_created)
		}

		return data_dict		


	def update(self,list_dicts,batch_size=200):
		'''
		Returns a dict of updated Ids failed to update Ids
		'''

		#List of records being updated
		records_to_update = [dic['Id'] for dic in list_dicts]

		#sforce Objects being updated
		sobjects = list(set([dic['type'] for dic in list_dicts]))

		batches = self._prep_data(list_dicts,batch_size)
		counter = 0

		#Salesforce time seems to be 15 seconds slower than UTC
		start_time = (datetime.utcnow() - timedelta(seconds=20)).strftime('%Y-%m-%dT%H:%M:%SZ')
		for batch in batches:
			counter+=1
			self.logger.info ('Updating batch %d of %d' % (counter,len(batches)))
			batch_result = self.svc.update(batch)

		end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

		records_updated = self._get_updated('Id',sobjects,start_time,end_time)
		records_not_updated = list(set(records_to_update) - set(records_updated))

		data_dict = {
		'success':records_updated,
		'errors':records_not_updated
		}

		return data_dict



	def upsert(self,upsert_field,list_dicts,batch_size=200):
		'''
		Dont use Id, use upsert_field as the unique identifier
		upsert_field must be a sforce custom external field
		Upserts only one object per call, since function is tied to the upsert field, 
		unlike the create or update operations
		'''

		#List of records being upserted
		records_to_upsert = [dic[upsert_field] for dic in list_dicts]

		#sforce Objects being upserted
		sobjects = list(set([dic['type'] for dic in list_dicts]))

		batches = self._prep_data(list_dicts,batch_size)
		counter = 0

		#Salesforce time seems to be 15 seconds slower than UTC
		start_time = (datetime.utcnow() - timedelta(seconds=20)).strftime('%Y-%m-%dT%H:%M:%SZ')
		for batch in batches:
			counter+=1
			self.logger.info ('Upserting batch %d of %d' % (counter,len(batches)))
			batch_result = self.svc.upsert(upsert_field,batch)

		end_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
	
		records_upserted = self._get_updated(upsert_field,sobjects,start_time,end_time)
		records_not_upserted = list(set(records_to_upsert) - set(records_upserted))

		data_dict = {
		'success':records_upserted,
		'errors':records_not_upserted
		}

		return data_dict	


	def delete(self,list_ids,batch_size=200):
		'''
		Input is a list, not a list of dicts
		List should contain only the Id of the record being deleted, no type
		'''

		counter = 0
		result = []

		for record_id in list_ids:
			counter+=1
			self.logger.info ('Deleting record %d of %d' % (counter,len(list_ids)))
			batch_result = self.svc.delete(record_id)
			result.append(batch_result)

		return result


