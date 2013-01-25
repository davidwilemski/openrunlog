
import datetime
from tornado import web, gen

import base
import models

class ProfileHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self, url):
        error = self.get_error()
        user = self.get_current_user()
        profile = models.User.objects(url=url).first()
        f1 = yield gen.Task(self.execute_thread, 
                models.Run.get_recent_runs, profile, 10)
        f2 = yield gen.Task(self.execute_thread, 
            models.Week.this_week, profile)
        f3 = yield gen.Task(self.execute_thread, 
            models.Run.this_week_mileage, profile)
        recent_runs = f1.result()
        week = f2.result()
        miles_this_week = f3.result()
        year = datetime.date.today().year

        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs, today=datetime.date.today().strftime("%x"), error=error, miles_this_week=miles_this_week, week=week, this_year=year, profile=profile)


class DashboardHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    @gen.engine
    def get(self):
        error = self.get_error()
        user = self.get_current_user()

        if user.public:
            self.redirect('/u/{}'.format(user.url))
            return

        f1 = yield gen.Task(self.execute_thread, 
                models.Run.get_recent_runs, user, 10)
        f2 = yield gen.Task(self.execute_thread, 
            models.Week.this_week, user)
        f3 = yield gen.Task(self.execute_thread, 
            models.Run.this_week_mileage, user)
        recent_runs = f1.result()
        week = f2.result()
        miles_this_week = f3.result()
        year = datetime.date.today().year

        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs, today=datetime.date.today().strftime("%x"), error=error, miles_this_week=miles_this_week, week=week, this_year=year, profile=user)
