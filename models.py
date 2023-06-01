from peewee import *

db = SqliteDatabase('db.db',)


class Person(Model):
    id = IntegerField(unique=True,index=True)
    model = TextField()
    jailbreak_chat_gpt = TextField()

    class Meta:
        database = db

