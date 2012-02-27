
from tornado import web

import base
import models

class DashboardHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        recent_runs = models.Run.objects(user=user)[:10]
        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs)
