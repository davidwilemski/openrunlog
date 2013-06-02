
import bcrypt


def hash_pwd(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_pwd(password, hashed):
    return bcrypt.hashpw(password, hashed) == hashed


def image_html(user, size='small'):
    """
    use robohash.org and have it default to gravatar if the user has one
    """
    if user.facebook:
        fbid = user.facebook['id']
        url = 'http://graph.facebook.com/{}/picture?type={}'.format(fbid, size)
    else:
        email = user.email
        if size == 'small':
            px = 50
        else:
            px = 180
        url = 'http://robohash.org/{}.jpg?gravatar=yes&size={}x{}'.format(
            email, px, px)
    html = '<img src="{}" />'.format(url)
    return html
