
import bcrypt


def hash_pwd(password):
    return bcrypt.hashpw(password, bcrypt.gensalt())


def check_pwd(password, hashed):
    return bcrypt.hashpw(password, hashed) == hashed


def fb_image_url(fbid, size='small'):
    url = 'https://graph.facebook.com/{}/picture?type={}'.format(fbid, size)

    if size != 'small':
        url = 'https://graph.facebook.com/{}/picture?width={}&height={}'.format(fbid, size, size)
    return url


def robohash_image_url(email, size='50'):
    url = 'https://robohash.org/{}.jpg?gravatar=yes&size={}x{}'.format(
        email, size, size)
    return url

def image_html(user, size):
    """
    use robohash.org and have it default to gravatar if the user has one
    """
    if user.facebook:
        fbid = user.facebook['id']
        url = fb_image_url(fbid, size)

    else:
        email = user.email

        if size == 'small' or size == 'square':
            size = 50
        else:
            size = 180

        url = robohash_image_url(email, size)

    html = '<img src="{}" />'.format(url)
    return html
