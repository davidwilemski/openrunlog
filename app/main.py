
import orl_settings

import sys
import mongoengine
from tornado import web, ioloop

application = web.Application([
    (r'/', 'home.HomeHandler'),
    (r'/login', 'login.LoginHandler'),
    (r'/logout', 'login.LogoutHandler'),
    (r'/register', 'login.RegisterHandler'),
    (r'/dashboard', 'dashboard.DashboardHandler'),
])

application.config = orl_settings.ORLSettings()

application.settings = {
        'debug': application.config.debug,
        'cookie_secret': application.config.cookie_secret,
        'template_path': 'templates/',
}


if __name__ == '__main__':
    port = 8888
    if len(sys.argv) > 1:
        port = sys.argv[1]

    mongoengine.connect(
            application.config.db_name, 
            host=application.config.db_host, 
            port=application.config.db_port, 
            username=application.config.db_username, 
            password=application.config.db_password)

    application.listen(port)
    ioloop.IOLoop.instance().start()

