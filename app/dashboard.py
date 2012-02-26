
from tornado import web

import base
import models

class DashboardHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        self.render('dashboard.html', page_title='Dashboard', user=user)
