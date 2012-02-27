
import mongoengine
import datetime

class User(mongoengine.Document):
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField()

class Run(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    date = mongoengine.DateTimeField(default=datetime.date.today())
    distance = mongoengine.DecimalField()
    time = mongoengine.StringField()
    notes = mongoengine.StringField()
