
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
