
import logging
import time
import urllib

import env
from tornado import auth, escape, gen, httpclient, web

import base
import models
import util


class LoginHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        user = yield self.get_current_user_async()
        if user is not None:
            self.redirect('/')
        self.render('login.html', page_title='Log In', user=None, error='')

    @web.asynchronous
    @gen.engine
    def post(self):
        email = self.get_argument('email', '').lower()
        password = self.get_argument('password', '')
        error = False

        if not email or not password:
            error = True

        user = yield models.get_user_by_email(self.redis, email)

        if not user:
            error = True

        t = time.time()
        if user and not util.check_pwd(password, user.password):
            error = True
        t2 = time.time()
        logging.debug('check_pwd took {}'.format(t2 - t))

        if error:
            error_text = "Yo! You gave an invalid username or incorrect password!"
            self.render('login.html', page_title='Log In',
                        user=None, error=error_text)
            self.tf.send({'users.logins.failure': 1}, lambda x: x)
            return

        cookie_args = {'httponly': True}

        logging.debug('request.protocol is {}'.format(self.request.protocol))
        if self.request.protocol == 'https':
            cookie_args['secure'] = True

        self.set_secure_cookie('user', str(user.id), **cookie_args)
        self.tf.send({'users.logins.success': 1}, lambda x: x)
        self.redirect('/')


class RegisterHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    def get(self):
        user = yield self.get_current_user_async()
        if user is not None:
            self.redirect('/')
        self.render('register.html', page_title='Register',
                    user=user, error='')

    @web.asynchronous
    @gen.coroutine
    def post(self):
        email = self.get_argument('email', '').lower()
        display_name = self.get_argument('display_name', '')
        password = self.get_argument('password', '')
        password_confirm = self.get_argument('password_confirm', '')
        url = self.get_argument('url', '').lower()
        public = True if self.get_argument('public', '') == 'yes' else False

        # check for general errors
        error = False
        if not email or not password or not password_confirm or not url:
            error = True
        if password != password_confirm:
            error = True
        if error:
            error_text = 'Missing a field or passwords do not match, all fields are required.'
            self.render('register.html', page_title='Register',
                        user=None, error=error_text)
            return

        # check that email hasn't already been used
        check_user = yield models.get_user_by_email(self.redis, email)
        if check_user:
            error_text = 'The email you tried already has an account. Please log in or register with a different email address.'
            self.render('register.html', page_title='Register',
                        user=None, error=error_text)
            return

        # make sure url is unique
        if url and not models.url_unique(url):
            error_text = 'A unique profile URL is required for public accounts!'
            self.render("register.html", page_title="Register",
                        user=None, error=error_text)

        new_user = models.User(email=email)
        new_user.password = util.hash_pwd(password)
        new_user.display_name = display_name
        new_user.url = url
        new_user.public = public
        new_user.save(self.redis)

        self.set_secure_cookie('user', str(new_user.id))
        self.tf.send({'users.registrations': 1}, lambda x: x)
        self.redirect('/')


class LogoutHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self):
        self.clear_cookie('user')
        yield gen.Task(self.tf.send, {'users.logouts': 1})
        self.redirect('/')


class SettingsHandler(base.BaseHandler):
    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def get(self):
        user = yield self.get_current_user_async()
        self.render("settings.html",
                    page_title="Settings for {}".format(user.display_name),
                    user=user, error=None)

    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def post(self):
        user = yield self.get_current_user_async()
        display_name = self.get_argument('displayname', '')
        public = self.get_argument('public', '')
        hashtags = self.get_argument('hashtags', '')

        if not display_name:
            error = 'A display name is required!'
            self.render("settings.html",
                        page_title="Settings for {}".format(user.display_name),
                        user=user, error=error)
            return

        public = True if public == 'yes' else False

        error = False
        if error:
            self.render("settings.html",
                        page_title="Settings for {}".format(user.display_name),
                        user=user, error=error)
            return

        user.public = public
        user.display_name = display_name
        user.hashtags = hashtags
        user.save(self.redis)

        yield gen.Task(self.tf.send, {'users.settings.changed': 1})
        self.redirect('/settings')


class FacebookHandler(base.BaseHandler, auth.FacebookGraphMixin):
    @web.authenticated
    @web.asynchronous
    @gen.coroutine
    def get(self):
        if self.get_argument("code", False):
            user = self.get_current_user()
            fbuser = yield self.get_authenticated_user(
                redirect_uri='http://openrunlog.org/auth/facebook',
                client_id=self.config["facebook_api_key"],
                client_secret=self.config["facebook_secret"],
                code=self.get_argument("code"))
            user.facebook = fbuser
            user.save(self.redis)
            self.redirect('/')
            yield gen.Task(self.tf.send, {'users.facebook.login': 1})

        else:
            self.authorize_redirect(
                redirect_uri='http://openrunlog.org/auth/facebook',
                client_id=self.config["facebook_api_key"],
                extra_params={"scope": "read_stream,offline_access"})
