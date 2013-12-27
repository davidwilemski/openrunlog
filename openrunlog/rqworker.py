import sys

import env
import mongoengine
import tornadotinyfeedback
from rq import Connection, Queue, Worker

import crosspost
import models


config = env.prefix('ORL_')
if config['debug'] == 'True':
    config['debug'] = True
else:
    config['debug'] = False

mongoengine.connect(
        config['db_name'], 
        host=config['db_uri'])

# Provide queue names to listen to as arguments to this script,
# similar to rqworker
with Connection():
    qs = map(Queue, sys.argv[1:]) or [Queue()]

    w = Worker(qs)
    w.work()

