import sqlite3

class db:
	_conn = None

	@classmethod
	def initDBCon(cls):
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
	def execute(cls, query, params = ()):
		return cls.getCursor().execute(query, params)

	@classmethod
	def getInteractionsBetween(cls, start, end):
		query = "SELECT size FROM interactions WHERE datetime >= ? AND datetime <= ?"

		return cls.execute(query, (start, end))

if __name__ == "__main__":
	db.execute("CREATE TABLE interactions (datetime datetime, url text, size bigint)")
	db.commit()
		
	