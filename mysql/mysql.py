import pymysql.cursors

class MySQL:
	def __init__(self,username,password,host,port):
		'''
		Connect to MySQL Database
		'''

		self.connection = pymysql.connect(
			host=host,
			port=port,
			user=username,
			password= password,
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor)

		self.cursor = self.connection.cursor()


	def get_schemas_tables(self):
		'''
		Get Schemas and Tables in the DB.
		Returns a dictionary of key = schema and value = list of tables
		'''

		self.cursor.execute("SHOW Databases")
		schemas_dict = self.cursor.fetchall()
		schemas = [schema['Database'] for schema in schemas_dict]

		schemas_tables = {}

		for schema in schemas:
			self.cursor.execute('USE %s' % schema)
			self.cursor.execute('SHOW Tables')
			tables_dict = self.cursor.fetchall()
			tables = [table['Tables_in_%s' % schema] for table in tables_dict]
			
			schemas_tables[schema] = tables

		return schemas_tables


	def build_query(self,schema,table):
		'''
		Generates a query string 
		'''

		query = "SELECT * FROM {0}.{1}".format(schema,table)

		return query


	def execute_query(self,query):
		'''
		Executes a query and returns a list of dicts
		'''
		
		try:
			self.cursor.execute(query)
		except Exception as e:
			return e

		result = self.cursor.fetchall()
		return result


	def close_connection(self):
		'''
		Closes the connection to the database
		'''
		self.cursor.close()
		self.connection.close()


'''
Example usage
'''

import os
from imp import load_source
import pandas as pd

if __name__ == '__main__':

	#Get credentials stored in home dir
	creds = load_source(u'credentials',
		os.path.normpath(os.path.expanduser(u'~/credentials.py')))
	
	#Connect to MySQL
	mysql = MySQL(creds.username,creds.password,creds.host,creds.port)

	#Get all schemas a tables
	schemas_tables = mysql.get_schemas_tables()

	#Loop through dict, and query each table
	#Store result in Dataframe and output as  csv
	for schema in schemas_tables:
		for table in schemas_tables[schema]:
			query = mysql.build_query(schema,table)
			query_result = mysql.execute_query(query)
			df = pd.DataFrame(query_result)
			if len(df) > 0:
				df.to_csv('{0}_{1}.csv'.format(schema,table),index=False)

	
	mysql.close_connection()
