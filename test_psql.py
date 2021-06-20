import psycopg2
import time

def connect():
	try:
		conn=None
		conn = psycopg2.connect(
			host="192.168.1.21",
			database='test2',
			user='pi',
			password='Tv8ams23061995')
		cur = conn.cursor()
		print('PostgreSQL database version : ')
		cur.execute('SELECT version()')
		db_version = cur.fetchone()
		print(db_version)
		return conn
	except (Exception, psycopg2.DatabaseError) as error:
		print(error)
	'''
	finally:
		if conn is not None:
			conn.close()
			print('Database connection closed')
	'''
conn = connect()

def loop():
	for a in range(0,100):
		sql_cmd="INSERT INTO assets(name,creation_time,creation_user,category_id) VALUES(%s,%s,%s,%s);"
		cursor = conn.cursor()
		cursor.execute(sql_cmd, ('aaa', 111.1, 'aaa', 2))
		conn.commit()

loop()
conn.close()