
from tornado import web, gen

import base
import models


class HomeHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self):
        user = yield self.get_current_user_async()
        if user is not None: # then redirect to dashboard
            self.redirect('/u/%s' % user.url)
            return

        yield gen.Task(self.tf.send, {'homepage.views': 1})
        self.render('home.html', page_title='Home', user=user, error='')
