
import datetime

import dateutil.parser
import dateutil.relativedelta
from tornado import auth, escape, gen, httpclient, web

import models
import base


class RecentRunsHandler(base.BaseHandler):
    @base.authorized_json_url
    @gen.coroutine
    def get(self, uri):
        self.tf.send({'profile.data.recentruns': 1}, lambda x: x)
        user = yield models.get_user_by_url(self.redis, uri)
        data = models.Run.get_recent_runs(user, 10)
        data = [x.public_dict() for x in data]
        self.finish({'data': data})


class ProfileHandler(base.BaseHandler):
    @base.authorized_json_url
    @gen.coroutine
    def get(self, uri):
        self.tf.send({'profile.data.profile': 1}, lambda x: x)
        user = yield models.get_user_by_url(self.redis, uri)
        self.finish(user.public_dict())


class SevenDayMileage(base.BaseHandler):
    @base.authorized_json_url
    @gen.coroutine
    def get(self, uri):
        self.tf.send({'profile.data.7daymileage': 1}, lambda x: x)
        user = yield models.get_user_by_url(self.redis, uri)
        date = self.get_argument('date', str(datetime.date.today()))

        try:
            date = dateutil.parser.parse(date)
        except ValueError, e:
            self.finish({'status': False})
            return

        mileage = user.mileage_seven_days(date)
        self.finish({'status': True, 'miles': mileage})
