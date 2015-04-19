
import env
import futures
import mongoengine
import redis
import rq
import setproctitle
import tornadoredis
import tornadotinyfeedback
from tornado import ioloop, web
from tornado.options import define, options, parse_command_line

import api

config = env.prefix('ORL_')
print(config)
if config['debug'] == 'True':
    config['debug'] = True
else:
    config['debug'] = False

settings = {
    'debug': config['debug'],
}

server_settings = {
    "xheaders": True,
}

application = web.Application([
    (r'/runs/([a-z]+)', api.AddRunHandler),
], **settings)

application.config = config
application.thread_pool = futures.ThreadPoolExecutor(max_workers=3)

if __name__ == '__main__':
    define('port', default=11001, help='TCP port to listen on')
    parse_command_line()
    setproctitle.setproctitle('orl.api')

    mongoengine.connect(
        config['db_name'],
        host=config['db_uri'])

    application.tf = tornadotinyfeedback.Client('openrunlog')
    application.redis = tornadoredis.Client()
    application.redis.connect()

    application.redis_sync = redis.StrictRedis()
    application.q = rq.Queue(connection=application.redis_sync)

    application.listen(options.port, **server_settings)
    ioloop.IOLoop.instance().start()
