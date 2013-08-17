
import datetime
from tornado import web, gen

import base
import models


class ProfileHandler(base.BaseHandler):
    @gen.coroutine
    @base.authorized
    def get(self, url):
        self.tf.send({'profile.dashboard.views': 1}, lambda x: x)
        error = self.get_error()
        user = yield self.get_current_user_async()
        profile = user

        # if we're not looking at our own
        # we show another profile if it's public
        if not user or user.url != url:
            profile = yield models.get_user_by_url(self.redis, url)

        recent_runs = yield self.execute_thread(
            models.Run.get_recent_runs, profile, 10)
        week = yield self.execute_thread(
            models.Week.this_week, profile)
        year = datetime.date.today().year

        self.render('dashboard.html', page_title='Dashboard', user=user, recent_runs=recent_runs, today=datetime.date.today().strftime("%x"), error=error, week=week, this_year=year, profile=profile)
