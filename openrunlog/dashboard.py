
import datetime
from tornado import web

import base
import models

class ProfileHandler(base.BaseHandler):
    @web.asynchronous
    def get(self, url):
        error = self.get_error()
        user = self.get_current_user()
        profile = models.User.objects(url=url).first()
        recent_runs = models.Run.objects(user=profile).order_by('-date')[:10]
        week = models.Week.this_week(profile)
        miles_this_week = models.Run.this_week_mileage(profile)
        year = datetime.date.today().year

        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs, today=datetime.date.today().strftime("%x"), error=error, miles_this_week=miles_this_week, week=week, this_year=year, profile=profile)


class DashboardHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        error = self.get_error()
        user = self.get_current_user()

        if user.public:
            self.redirect('/u/{}'.format(user.url))

        recent_runs = models.Run.objects(user=user).order_by('-date')[:10]
        week = models.Week.this_week(user)
        miles_this_week = models.Run.this_week_mileage(user)
        year = datetime.date.today().year

        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs, today=datetime.date.today().strftime("%x"), error=error, miles_this_week=miles_this_week, week=week, this_year=year, profile=user)
