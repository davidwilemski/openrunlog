
import bcrypt
import hashlib

def hash_pwd(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_pwd(password, hashed):
    return bcrypt.hashpw(password, hashed) == hashed

def validate_time(time):
    return True 

def gravatar_html(email, size=15):
    h = hashlib.md5(email.lower()).hexdigest()
    html = '<img src="http://www.gravatar.com/avatar/{}.jpg?s={}" />'.format(h, size)
    return html

