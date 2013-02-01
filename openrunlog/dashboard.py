
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
        profile = user

        # if we're not looking at our own, we show another profile if it's public
        if user.url != url:
            other_user = models.User.objects(url=url).first()
            if other_user and other_user.public:
                profile = other_user
            else:
                self.redirect('/u/%s' % user.url)

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
