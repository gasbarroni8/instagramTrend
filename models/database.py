import pymysql

class DataBase:

	def __init__(self, host, port, user, passwd, db="mysql", charset='utf8mb4'):

		self.conn = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db, charset=charset)							   
		self.cur = self.conn.cursor()

		print(self.conn.open)


	def use_table(self, tableName):

		self.cur.execute("USE "+tableName)


	def execution(self):
			
		self.cur.execute(self.sql)

		try:
			self.conn.commit()       
		except:
			self.conn.rollback()

	def executemany(self, sql, args):

		self.cur.executemany(sql, args)

		try:
			self.conn.commit()       
		except:
			self.conn.rollback()

	def fetch(self, fetch):

		if fetch == 'one':
			return self.getAlone(self.cur.fetchone())
		else:
			return self.cur.fetchall()


	def getAlone(self, fetchdata):

		try:
			if len(fetchdata) == 1:
				fetchdata = fetchdata[0]
		except:
			pass
			
		return fetchdata


	def getInsterId(self):

		return self.cur.lastrowid

	def table(self, tableName):

		self.tableName = tableName

	def where(self, *args):

		self.sql += "WHERE %s %s '%s'" % (args[0], args[1], args[2])
		# print(self.sql)

	def select(self, *args):

		self.sql = "SELECT "

		if args:
			for arg in args:
				self.sql += arg + ", "
			self.sql = self.sql[:-2]
		else:
			self.sql += "*"

		self.sql += " FROM " + self.tableName + " "

	def insert(self, **kwargs):
		
		self.sql = "INSERT INTO " + self.tableName + " "

		keys = tuple()
		values = tuple()

		for k, v in kwargs.items():
			keys += (tuple([k]))
			values += tuple([v])

		self.sql += str(keys).replace("'","`") + " VALUES " + str(values)

	def update(self, **kwargs):

		self.sql = "UPDATE " + self.tableName + " SET "

		if kwargs:
			for k, v in kwargs.items():
				self.sql += "`" + k + "` = '%s', " % (v) 

			self.sql = self.sql[:-2] + " "

	def delete(self):
		
		self.sql = "DELETE FROM " + self.tableName + " "
