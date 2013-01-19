
import env
import sys
import os
import mongoengine
from tornado import web, ioloop, process
from tornado.options import define, options, parse_command_line

import home
import login
import dashboard
import data
import runs


config = env.prefix('ORL_')
print config
if config['debug'] == 'True':
    config['debug'] = True
else:
    config['debug'] = False

settings = {
        'debug': config['debug'],
        'cookie_secret': config['cookie_secret'],
        'template_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
        'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
        'login_url': '/login',
}

application = web.Application([
    (r'/', home.HomeHandler),
    (r'/login', login.LoginHandler),
    (r'/logout', login.LogoutHandler),
    (r'/register', login.RegisterHandler),
    (r'/settings', login.SettingsHandler),
    (r'/dashboard', dashboard.DashboardHandler),
    (r'/u/([a-zA-Z0-9]+)', dashboard.ProfileHandler),
    (r'/add', runs.AddRunHandler),
    (r'/data/([A-Za-z0-9]{24})/this_week', data.ThisWeekHandler),
    (r'/data/([A-Za-z0-9]{24})/mileage/weekly', data.WeeklyMileageHandler),
], **settings)

application.config = config


if __name__ == '__main__':
    define('port', default=11000, help='TCP port to listen on')
    parse_command_line()

    mongoengine.connect(
            config['db_name'], 
            host=config['db_uri'])

    if not config['debug']:
        process.fork_processes(process.cpu_count()*2 + 1)
    application.listen(options.port)
    ioloop.IOLoop.instance().start()

