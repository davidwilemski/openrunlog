
import datetime
from dateutil.relativedelta import relativedelta
import env
import logging
import mongoengine
from openrunlog import models, constants
from tornado import ioloop, gen
import tornadotinyfeedback


def _daily_active_query():
    yesterday = datetime.datetime.today()-relativedelta(days=1)
    today_runs = models.Run.objects(date__gte=yesterday)
    users = set()

    for run in today_runs:
        users.add(run.user)
    num = len(users)
    return num


@gen.coroutine
def daily_active():
    logging.info('sending users.active.daily')
    yield gen.Task(tf.send, {'users.active.daily': _daily_active_query()})


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
