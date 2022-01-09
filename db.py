import sqlite3

class db:
	_conn = None

	@classmethod
	def initDBCon(cls):
		print("initing")
		
		return sqlite3.connect("interactions.db")

	@classmethod
	def getCon(cls):
		if not cls._conn:
			cls._conn = cls.initDBCon()
		return cls._conn

	@classmethod
	def getCursor(cls):
		return cls.getCon().cursor()

	@classmethod
	def commit(cls):
		return cls.getCon().commit()

	@classmethod
	def execute(cls, query):
		return cls.getCursor().execute(query)


db.execute("CREATE TABLE interactions (datetime datetime)")
db.execute("CREATE TABLE interaction (datetime datetime)")
db.execute("CREATE TABLE interactio (datetime datetime)")