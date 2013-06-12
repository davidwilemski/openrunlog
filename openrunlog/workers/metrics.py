
import datetime
import env
import logging
import mongoengine
from openrunlog import models, constants
from tornado import ioloop, gen
import tornadotinyfeedback


def _daily_active_query():
    # TODO instead query in last 24 hours instead of .today() 
    # so that we don't get drop offs around date changes
    today_runs = models.Run.objects(date=datetime.datetime.today())
    users = set()

    for run in today_runs:
        users.add(run.user)
    num = len(users)
    logging.info('found {} users active today'.format(num))
    return num


@gen.coroutine
def daily_active():
    logging.info('sending users.active.daily')
    yield tf.send({'users.active.daily': _daily_active_query()})


def main():
    logging.info('starting active daily user counter')
    ioloop.PeriodicCallback(daily_active, 60*1000).start()


if __name__ == '__main__':
    config = env.prefix('ORL_')
    if config['debug'] == 'True':
        config['debug'] = True
    else:
        config['debug'] = False

    mongoengine.connect(
        config['db_name'],
        host=config['db_uri'])
    tf = tornadotinyfeedback.Client('openrunlog')
    logging.basicConfig(level=logging.INFO)

    logging.info('starting workers.metrics')
    main()

    ioloop.IOLoop.instance().start()