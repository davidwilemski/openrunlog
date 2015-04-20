import functools
import logging
import urllib

from tornado import gen, web
from tornado.ioloop import IOLoop

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
        for k, v in params.iteritems():
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
    def redis_sync(self):
        self.tf.send({'redis.getconnection': 1}, lambda x: x)
        return self.application.redis_sync

    @property
    def q(self):
        self.tf.send({'rq.getq': 1}, lambda x: x)
        return self.application.q

    @property
    def config(self):
        return self.application.config

    def write_error(self, status_code, **kwargs):
        """custom error pages"""
        import traceback

        if status_code == 404:
            message = ['Sorry, we could not find that page.', '']
            self.tf.send({'error.4xx': 1}, lambda x: x)
        else:
            self.tf.send({'error.5xx': 1}, lambda x: x)
            message = [
                'Sorry, what you have come across has created an error. The hampsters are running in the back to try and fix it as soon as possible.',
                ''
            ]

        if self.settings.get('debug') and 'exc_info' in kwargs:
            # we are in debug mode and have errors to show
            for line in traceback.format_exception(*kwargs['exc_info']):
                message += [line]
        self.render('error.html',
                    page_title='Error Page',
                    user=self.get_current_user(),
                    message=message,
                    error=None)


class ErrorHandler(BaseHandler):
    """Generates an error response with ``status_code`` for all requests."""

    def initialize(self, status_code):
        self.set_status(status_code)

    def prepare(self):
        raise web.HTTPError(self._status_code)

    def check_xsrf_cookie(self):
        pass


def authorized_json(method, *args):
    """Decorate API methods with this to require that the user be logged in."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        uid = args[0]
        user = self.get_current_user()
        datauser = models.User.objects(id=uid).first()
        if not datauser:
            raise web.HTTPError(403)
        if not datauser.public and (not user or user.email != datauser.email):
            raise web.HTTPError(403)
        return method(self, *args, **kwargs)

    return wrapper


def authorized_json_url(method, *args):
    """Decorate API methods with this to require that the user be logged in."""

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        url = args[0]
        user = self.get_current_user()
        datauser = models.User.objects(url=url).first()
        if not datauser:
            raise web.HTTPError(403)
        if not datauser.public and (not user or user.email != datauser.email):
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

        if not profile:
            self.send_error(404)
            return

        if not profile.public and (not user or user.url != profile.url):
            return self.render('private.html',
                               page_title='Private Profile',
                               user=user,
                               profile=profile,
                               error=None)

        return method(self, *args, **kwargs)

    return wrapper


def authenticated_async(f):
    @functools.wraps(f)
    @gen.coroutine
    def wrapper(self, *args, **kwargs):
        self._auto_finish = False
        self.current_user = yield self.get_current_user_async()
        if not self.current_user:
            self.redirect(self.get_login_url() + '?' +
                          urllib.urlencode(dict(next=self.request.uri)))
        else:
            f(self, *args, **kwargs)

    return wrapper


class API(BaseHandler):
    def write_error(self, status_code, **kwargs):
        self.set_header('Content-Type', 'application/json')
        if 'exc_info' in kwargs:
            exception = kwargs['exc_info'][1]
            return self.finish(
                {'error': str(exception),
                 'code': status_code})
        self.finish({'error': 'unknown error', 'code': status_code})
