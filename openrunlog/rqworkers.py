
import logging

import redis
import requests
import tornadoredis
from rq.decorators import job

import crosspost
import models


r = redis.StrictRedis(host='localhost', port=6379)

@job('normal', connection=r)
def calculate_streaks(user):
    if not user:
        return

    r = tornadoredis.Client()
    r.connect()
    user.calculate_streaks(r)


@job('normal', connection=r)
def crosspost_run(run):
    crosspost.export_run(run)


@job('normal', connection=r)
def crosspost_user(user):
    runs = models.Run.objects(user=user)

    for run in runs:
        if not run.exported_to_dailymile:
            crosspost_run.delay(run)
