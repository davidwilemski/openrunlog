
from tornado import web

import base
import models

class HomeHandler(base.BaseHandler):
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        if user is not None: # then redirect to dashboard
            self.redirect('/dashboard')
            return

        self.render('home.html', page_title='Home', user=user)
