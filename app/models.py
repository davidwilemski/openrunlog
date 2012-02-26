
import mongoengine

class User(mongoengine.Document):
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField()
