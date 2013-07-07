
import datetime
from dateutil.relativedelta import relativedelta
import env
import logging
import mongoengine
from openrunlog import models
import setproctitle
from tornado import ioloop, gen
import tornadotinyfeedback


def _daily_active_query():
    # TODO figure out why 27? timezones I'm guessing, still doesn't make sense
    yesterday = datetime.datetime.today()-relativedelta(hours=27)
    today_runs = models.Run.objects(date__gte=yesterday)
    users = set()

    for run in today_runs:
        users.add(run.user)
    num = len(users)
    return num


def _monthly_active_query():
    # TODO figure out why 27? timezones I'm guessing, still doesn't make sense
    monthly = datetime.datetime.today()-relativedelta(hours=27)
    runs = models.Run.objects(date__gte=monthly)
    users = set()

    for run in runs:
        users.add(run.user)
    num = len(users)
    return num

@gen.coroutine
def active_users():
    logging.info('sending users.active.daily')
    yield gen.Task(tf.send, {'users.active.daily': _daily_active_query()})
    yield gen.Task(tf.send, {'users.active.monthly': _monthly_active_query()})


def main():
    logging.info('starting active user counter')
    ioloop.PeriodicCallback(active_users, 60*1000).start()


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
    setproctitle.setproctitle('orl.workers.metrics')

    logging.info('starting workers.metrics')
    main()

    ioloop.IOLoop.instance().start()
