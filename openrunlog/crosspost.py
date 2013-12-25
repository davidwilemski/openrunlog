
import logging

from tornado import gen

import models


dailymile_export = 'orl:dailymile:export'


def send_user(r, user):
    runs = models.Run.objects(user=user)
    for run in runs:
        if not run.exported_to_dailymile and run.distance > 0:
            logging.debug('queueing run of {} miles'.format(run.distance))
            r.rpush(dailymile_export, str(run.id))


@gen.engine
def send_run(r, run):
    r.rpush(dailymile_export, str(run.id))


@gen.engine
def get(r, callback):
    run = yield gen.Task(r.blpop, dailymile_export)
    run = run[dailymile_export]
    callback(run)

