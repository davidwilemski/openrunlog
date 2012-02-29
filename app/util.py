
import bcrypt
import md5

def hash_pwd(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_pwd(password, hashed):
    return bcrypt.hashpw(password, hashed) == hashed

def validate_time(time):
    return True 

# XXX md5 module deprecated, use hashlib
def gravatar_html(email):
    h = md5.md5(email.lower()).hexdigest()
    html = '<img src="http://www.gravatar.com/avatar/%s.jpg?s=15" />' % h
    return html
