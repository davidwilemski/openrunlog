
import bcrypt

def hash_pwd(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())

def check_pwd(password, hashed):
    return bcrypt.hashpw(password, hashed) == hashed
