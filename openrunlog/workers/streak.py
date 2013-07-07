
import env
import logging
from openrunlog import models, constants
import redis
import setproctitle
import mongoengine


def main(r):
    while True:
        key, userid = r.blpop(constants.calculate_streaks)
        user = models.User.objects(id=userid).first()
        calculate_streaks(user)
        logging.info('computed streaks for {}'.format(user.display_name))
        logging.info(user.streaks)


def calculate_streaks(user):
    if not user:
        return

    user.calculate_streaks()

if __name__ == '__main__':
    config = env.prefix('ORL_')
    if config['debug'] == 'True':
        config['debug'] = True
    else:
        config['debug'] = False
    mongoengine.connect(
        config['db_name'],
        host=config['db_uri'])
    r = redis.StrictRedis(host='localhost', port=6379)

    logging.basicConfig(level=logging.INFO)
    setproctitle.setproctitle('orl.workers.streak')

    main(r)
