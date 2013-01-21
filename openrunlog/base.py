import functools
import futures
from tornado import web
from tornado.stack_context import ExceptionStackContext
import urllib

import models

class BaseHandler(web.RequestHandler):
    def get_current_user(self):
        uid = self.get_secure_cookie('user')
        if uid is None:
            return None

        user = models.User.objects(id=uid).first()
        return user

    def redirect_msg(self, url, params):
        for k,v in params.iteritems():
            self.set_cookie('msg_' + k, urllib.quote(v))
        self.redirect(url)

    def get_error(self):
        error = urllib.unquote(self.get_cookie('msg_error', ''))
        if error:
            self.clear_cookie('msg_error')
        return error

    @property
    def thread_pool(self):
        return self.application.thread_pool
