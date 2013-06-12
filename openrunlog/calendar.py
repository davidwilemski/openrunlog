
import datetime
from tornado import web, gen

import base
import models


class CalendarHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    @base.authorized
    def get(self, url):
        self.tf.send({'profile.calendar.views': 1}, lambda x: x)
        error = self.get_error()
        user = self.get_current_user()
        profile = user

        # if we're not looking at our own
        # we show another profile if it's public
        if not user or user.url != url:
            profile = models.User.objects(url=url).first()

        #calendar_runs = yield self.execute_thread(
        #    models.Run.get_calendar_runs, profile)
        calendar_runs = models.Run.get_calendar_runs(profile)

        self.render('calendar.html', page_title='Calendar', user=user, today=datetime.date.today().strftime("%x"), this_year=datetime.date.today().year, error=error, profile=profile, calendar_runs=calendar_runs)
