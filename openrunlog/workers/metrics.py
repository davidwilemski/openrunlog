
import datetime
from dateutil.relativedelta import relativedelta
import env
import logging
import mongoengine
from openrunlog import models
import setproctitle
import time
from tornado import ioloop, gen
import tornadotinyfeedback


def timestamp_to_oid(timestamp):
    return '{0:x}0000000000000000'.format(timestamp)


def _daily_active_query():
    yesterday = timestamp_to_oid(time.time() - 60*60*24)
    today_runs = models.Run.objects(id__gte=yesterday)
    users = set()

    for run in today_runs:
        users.add(run.user)
    num = len(users)
    logging.info("daily active users: {}".format(num))
    return num


def _monthly_active_query():
    monthly = timestamp_to_oid(time.time() - 60*60*24*30)
    runs = models.Run.objects(id__gte=monthly)
    users = set()

    for run in runs:
        users.add(run.user)
    num = len(users)
    print num
    logging.info("monthly active users: {}".format(num))
    return num

@gen.coroutine
def active_users():
    logging.info('{} sending users.active'.format(datetime.datetime.today()))
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
