
import bcrypt


def hash_pwd(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_pwd(password, hashed):
    return bcrypt.hashpw(password, hashed) == hashed


def gravatar_html(email, size=15):
    """
    use robohash.org and have it default to gravatar if the user has one
    """
    html = '<img src="http://robohash.org/{}.jpg?gravatar=yes&size={}x{}" />'.format(
        email, size, size)
    return html
