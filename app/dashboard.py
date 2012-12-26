
import datetime
from tornado import web

import base
import models

class DashboardHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        recent_runs = models.Run.objects(user=user)[:10]
        miles_this_week = models.Run.this_week_mileage(user)
        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs, today=datetime.date.today().strftime("%x"), error='', miles_this_week=miles_this_week)
