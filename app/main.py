
import orl_settings

import sys
import os
import mongoengine
from tornado import web, ioloop, process
from tornado.options import define, options, parse_command_line

config = orl_settings.ORLSettings()
settings = {
        'debug': config.debug,
        'cookie_secret': config.cookie_secret,
        'template_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates"),
        'static_path': os.path.join(os.path.dirname(os.path.abspath(__file__)), "static"),
        'login_url': '/login',
}

application = web.Application([
    (r'/', 'home.HomeHandler'),
    (r'/login', 'login.LoginHandler'),
    (r'/logout', 'login.LogoutHandler'),
    (r'/register', 'login.RegisterHandler'),
    (r'/dashboard', 'dashboard.DashboardHandler'),
    (r'/add', 'runs.AddRunHandler'),
    (r'/data/this_week', 'data.ThisWeekHandler'),
    (r'/data/mileage/weekly', 'data.WeeklyMileageHandler'),
], **settings)

application.config = config



if __name__ == '__main__':
    define('port', default=11000, help='TCP port to listen on')
    parse_command_line()

    mongoengine.connect(
            config.db_name, 
            host=config.db_uri)

    if not config.debug:
        process.fork_processes(process.cpu_count()*2 + 1)
    application.listen(options.port)
    ioloop.IOLoop.instance().start()

