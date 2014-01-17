
import os

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

import calendar
import dashboard
import data
import groups
import profiledata
import home
import jsx
import login
import racelog
import runs
from base import ErrorHandler


config = env.prefix('ORL_')
print config
if config['debug'] == 'True':
    config['debug'] = True
else:
    config['debug'] = False

settings = {
    'debug': config['debug'],
    'cookie_secret': config['cookie_secret'],
    'template_path': os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "templates"),
    'static_path': os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "static"),
    'login_url': '/login',
    'static_handler_class': jsx.JSXStaticFileHandler,
}

server_settings = {
    "xheaders": True,
}

web.ErrorHandler = ErrorHandler

application = web.Application([
    (r'/', home.HomeHandler),
    (r'/login', login.LoginHandler),
    (r'/logout', login.LogoutHandler),
    (r'/register', login.RegisterHandler),
    (r'/settings', login.SettingsHandler),
    (r'/settings/dailymile/noexport', login.DailyMileLogoutHandler),
    (r'/auth/dailymile', login.DailyMileHandler),
    (r'/auth/facebook', login.FacebookHandler),
    (r'/u/([a-zA-Z0-9_]+)', dashboard.ProfileHandler),
    (r'/u/([a-zA-Z0-9_]+)/calendar', calendar.CalendarHandler),
    (r'/u/([a-zA-Z0-9_]+)/calendar/miles', calendar.CalendarMilesHandler),
    (r'/u/([a-zA-Z0-9_]+)/races', racelog.AllRacesHandler),
    (r'/u/([a-zA-Z0-9_]+)/races/([A-Za-z0-9]{24})', racelog.ShowRaceHandler),
    (r'/u/([a-zA-Z0-9_]+)/runs', runs.AllRunsHandler),
    (r'/u/([a-zA-Z0-9_]+)/run/([A-Za-z0-9]{24})', runs.ShowRunHandler),
    (r'/u/([A-Za-z0-9]+)/data/recent.json', profiledata.RecentRunsHandler),
    (r'/g', groups.GroupDashboardHandler),
    (r'/g/([a-zA-Z0-9_]+)', groups.GroupHandler),
    (r'/add', runs.AddRunHandler),
    (r'/remove', runs.RemoveRunHandler),
    (r'/data/([A-Za-z0-9]{24})/this_week', data.ThisWeekHandler),
    (r'/data/([A-Za-z0-9]{24})/recent', data.RecentRunsHandler),
    (r'/data/([A-Za-z0-9]{24})/mileage/weekly', data.WeeklyMileageHandler),
    (r'/data/([A-Za-z0-9]{24})/runs/weekday', data.WeekdayRunsHandler),
    (r'/data/([A-Za-z0-9]{24})/runs/year', data.DailyRunsHandler),
    (r'/data/([A-Za-z0-9]{24})/runs/month', data.MonthRunsHandler),
    #(r'/jsx/(.*)', jsx.JSXStaticFileHandler, {'path': JSXPATH}),
], **settings)

application.config = config
application.thread_pool = futures.ThreadPoolExecutor(max_workers=3)


if __name__ == '__main__':
    define('port', default=11000, help='TCP port to listen on')
    parse_command_line()
    setproctitle.setproctitle('orl.app')

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
