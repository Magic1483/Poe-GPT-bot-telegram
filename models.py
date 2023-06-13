from peewee import *

db = SqliteDatabase('db.db',)


class Person(Model):
    id = IntegerField(unique=True,index=True)
    model = TextField()
    generate_type = TextField(default='text')#img or text
    jailbreak_chat_gpt = TextField()

    class Meta:
        database = db

