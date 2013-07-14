
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
    return '{0:x}0000000000000000'.format(int(timestamp))


def _daily_timestamp():
    yesterday = timestamp_to_oid(time.time() - 60*60*24)
    return yesterday


def _weekly_timestamp():
    weekly = timestamp_to_oid(time.time() - 60*60*24*7)
    return weekly 


def _monthly_timestamp():
    monthly = timestamp_to_oid(time.time() - 60*60*24*30)
    return monthly


def _active_users_query(timestamp):
    runs = models.Run.objects(id__gte=timestamp)
    users = set()
    
    for run in runs:
        users.add(run.user)
    num = len(users)
    return num

@gen.coroutine
def active_users():
    logging.info('{} sending users.active'.format(datetime.datetime.today()))

    daily_users = _active_users_query(_daily_timestamp())
    yield gen.Task(tf.send, {'users.active.daily': daily_users})
    logging.info("daily active users: {}".format(daily_users))

    weekly_users = _active_users_query(_weekly_timestamp())
    yield gen.Task(tf.send, {'users.active.weekly': weekly_users})
    logging.info("weekly active users: {}".format(weekly_users))

    monthly_users = _active_users_query(_monthly_timestamp())
    yield gen.Task(tf.send, {'users.active.monthly': monthly_users})
    logging.info("monthly active users: {}".format(monthly_users))


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
