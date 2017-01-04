import pymysql.cursors
from sshtunnel import SSHTunnelForwarder


class MySQL:

	def __init__(self,host,ssh_port=22,ssh_username,ssh_private_key,
		remote_bind_ip,remote_bind_port=3306,db_username,db_password):
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