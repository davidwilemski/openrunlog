
import env
import logging
import tornado.ioloop
import tornado.options
import tornado.gen
import tornado.httpclient
import tornadoredis
import tornadotinyfeedback
import mongoengine
import json

import crosspost
import models

tf = tornadotinyfeedback.Client('openrunlog')

@tornado.gen.engine
def run_exporter(r):
    logging.debug('starting worker...')
    while True:
        logging.debug('waiting for run in queue...')
        run = yield tornado.gen.Task(crosspost.get, r)
        export_run(run)

@tornado.gen.engine
def export_run(run):
    run = models.Run.objects(id=run).first()

    if run.exported_to_dailymile:
        return

    logging.debug('exporting {} mile run'.format(
        run.distance))

    url = 'https://api.dailymile.com/entries.json?oauth_token={}'.format(run.user.dailymile_token)

    body = {
            'message': run.notes,
            'workout': {
                'distance': {
                    'value': run.distance ,
                    'units': 'miles',
                    'duration': run.time
                },
                'activity_type': 'running',
                'completed_at': run.date.isoformat(),
            }
    }

    headers = {
            'Content-Type': 'application/json'
    }

    client = tornado.httpclient.AsyncHTTPClient()
    response = yield tornado.gen.Task(client.fetch, url, method='POST', body=json.dumps(body), headers=headers)
    logging.debug(body)
    logging.debug(response)
    tf.send({'users.dailymile.run.sent': 1}, lambda x: x)

    if response.code == 201:
        run.exported_to_dailymile = True
        run.save()


if __name__ == '__main__':
    config = env.prefix('ORL_')
    if config['debug'] == 'True':
        config['debug'] = True
    else:
        config['debug'] = False

    r = tornadoredis.Client()
    r.connect()
    mongoengine.connect(
            config['db_name'], 
            host=config['db_uri'])

    tornado.options.parse_command_line()
    run_exporter(r)
    tornado.ioloop.IOLoop.instance().start()
