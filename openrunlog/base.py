import functools
import futures
import logging
from tornado import web, concurrent
from tornado.ioloop import IOLoop
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

    @property
    def executor(self):
        return self.application.thread_pool

    def execute_thread(self, fn, *args, **kwargs):
        callback = kwargs.pop('callback', None)
        future = self.thread_pool.submit(fn, *args)
        if callback:
            future.add_done_callback(
                lambda future: IOLoop.instance().add_callback(
                    functools.partial(callback, future)))
        return future

    @property
    def redis(self):
        self.tf.send({'redis.getconnection': 1}, lambda x: x)
        return self.application.redis

    @property
    def tf(self):
        return self.application.tf
    
    @property
    def config(self):
        return self.application.config


def authorized_json(method, *args):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        uid = args[0]
        user = self.get_current_user()
        data_user = models.User.objects(id=uid).first()
        if not data_user.public and (not user or user.email != data_user.email):
            raise web.HTTPError(403)
        return method(self, *args, **kwargs)
    return wrapper


def authorized(method, *args):
    """Decorate methods with this to require that the user be logged in."""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        url = args[0]
        logging.debug(args)
        profile = models.User.objects(url=url).first()
        user = self.get_current_user()
        if not profile.public and (not user or user.url != profile.url):
            return self.render(
                'private.html',
                page_title='Private Profile',
                user=user, profile=profile, error=None)

        return method(self, *args, **kwargs)
    return wrapper
