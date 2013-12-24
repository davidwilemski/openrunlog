import functools
import futures
import logging
from tornado import web, concurrent, gen
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

    @gen.coroutine
    def get_current_user_async(self):
        uid = self.get_secure_cookie('user', None)
        logging.debug('current_user_async {}'.format(uid))
        if uid:
            user = yield models.get_user_by_uid(self.redis, uid)
            raise gen.Return(user)
        raise gen.Return(None)


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

    def write_error(self, status_code, **kwargs):
        """custom error pages"""
        import traceback
        self.tf.send({'error.5xx': 1}, lambda x: x)
        message = ['Sorry, what you have come across has created an error. The hampsters are running in the back to try and fix it as soon as possible.', '']
        if self.settings.get('debug') and 'exc_info' in kwargs:
            # we are in debug mode and have errors to show
            for line in traceback.format_exception(*kwargs['exc_info']):
                message += [line]
        self.render('error.html', page_title='Error Page', user=self.get_current_user(), message=message, error=None)

class ErrorHandler(BaseHandler):
    """Generates an error response with ``status_code`` for all requests."""
    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        raise web.HTTPError(self._status_code)

    def check_xsrf_cookie(self):
        pass

    def write_error(self, status_code, **kwargs):
        import traceback
        self.tf.send({'error.4xx': 1}, lambda x: x)
        message = ['Sorry, we could not find that page.', '']
        if self.settings.get('debug') and 'exc_info' in kwargs:
            # we are in debug mode and have errors to show
            for line in traceback.format_exception(*kwargs['exc_info']):
                message += [line]
        self.render('error.html', page_title='Error Page', user=self.get_current_user(), message=message, error=None)

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


def authenticated_async(f):
    @functools.wraps(f)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        self.current_user = yield self.get_current_user_async()
        if not self.current_user:
            self.redirect(
                self.get_login_url() + '?' +
                urllib.urlencode(dict(next=self.request.uri)))
        else:
            f(self, *args, **kwargs)
    return wrapper
