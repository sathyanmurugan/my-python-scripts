import pymysql
import pymysql.cursors
from sshtunnel import SSHTunnelForwarder

class MySQL(object):

	def __init__(self,username,password,host,port):
		'''
		Connect to MySQL Database
		'''
		# Set dictinary type for cursor to OrderedDict
		pymysql.cursors.DictCursor.dict_type = OrderedDict
		self.connection = pymysql.connect(
			host=host,
			port=port,
			user=username,
			password= password,
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor)

		self.cursor = self.connection.cursor()
	
	def __enter__(self):
		
		return self


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


	def execute_query(self,query):
		'''
		Executes a query and returns a list of dicts
		'''
		
		try:
			self.cursor.execute(query)
			self.connection.commit()
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

	def __exit__(self,*args):
		self.close_connection()





class MySQLSSH(MySQL):

	def __init__(self,host,ssh_port,ssh_username,ssh_private_key,
		remote_bind_ip,remote_bind_port,db_username,db_password):
		'''
		1. SSH Tunnel into a specified host and port forward 
		2. Connect to the MySQL Database
		'''

		self.server = SSHTunnelForwarder((host,ssh_port),
			ssh_username=ssh_username,
			ssh_private_key=ssh_private_key,
			remote_bind_address=(remote_bind_ip, remote_bind_port))

		self.server.start()

		self.cnxn = pymysql.connect(
			host='127.0.0.1',
			port=self.server.local_bind_port,
			user=db_username,
			password=db_password,
			charset='utf8mb4',
			cursorclass=pymysql.cursors.DictCursor)

		self.cursor = self.cnxn.cursor()

	
	def close_connection(self):
		self.cursor.close()
		self.cnxn.close()
		self.server.close()