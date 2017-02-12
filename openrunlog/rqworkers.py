
import logging

import redis
import requests
import tornadoredis
from rq.decorators import job

import models


r = redis.StrictRedis(host='localhost', port=6379)

@job('normal', connection=r)
def calculate_streaks(user):
    if not user:
        return

    r = tornadoredis.Client()
    r.connect()
    user.calculate_streaks(r)
