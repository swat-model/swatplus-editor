from peewee import (
    SqliteDatabase,
    Model
)

db = SqliteDatabase(None)


class BaseModel(Model):
	class Meta:
		database = db
