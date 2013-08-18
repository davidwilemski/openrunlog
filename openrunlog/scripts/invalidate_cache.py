
import env
import mongoengine
from openrunlog import models, cache
import tornado.ioloop
import tornadoredis


def invalidate(r):
    for user in models.User.objects():
        cache.invalidate(r, user)
    tornado.ioloop.IOLoop.instance().stop()

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
    invalidate(r)

    tornado.ioloop.IOLoop.instance().start()
