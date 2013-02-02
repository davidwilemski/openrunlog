
import datetime
from tornado import web, gen

import base
import models

class ProfileHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self, url):
        self.tf.send({'profile.dashboard.views': 1}, lambda x: x)
        error = self.get_error()
        user = self.get_current_user()
        profile = user

        # if we're not looking at our own, we show another profile if it's public
        if not user or user.url != url:
            profile = models.User.objects(url=url).first()
            if not profile.public:
                self.render('private.html', page_title='Private Profile', user=user, profile=profile, error=None)

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
