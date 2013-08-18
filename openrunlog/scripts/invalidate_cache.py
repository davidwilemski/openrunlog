
import env
import mongoengine
from openrunlog import models, cache
import tornadoredis

if __name__ == '__main__':
    config = env.prefix('ORL_')
    if config['debug'] == 'True':
        config['debug'] = True
    else:
        config['debug'] = False
    mongoengine.connect(
        config['db_name'],
        host=config['db_uri'])

    r = tornadoredis.Client()
    r.connect()

    for user in models.User.objects():
        cache.invalidate(r, user)
