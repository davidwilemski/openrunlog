
import logging
from tornado import web, auth, httpclient, gen, escape

import base
import crosspost
import env
import models
import time
import urllib
import util

class LoginHandler(base.BaseHandler):
    @web.asynchronous
    def get(self):
        if self.get_current_user() is not None:
            self.redirect('/')
        self.render('login.html', page_title='Log In', user=None, error='')

    @web.asynchronous
    @gen.engine
    def post(self):
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')
        error = False

        if not email or not password:
            error = True

        user = models.User.objects(email=email).first()

        if not user:
            error = True

        t = time.time()
        if user and not util.check_pwd(password, user.password):
            error = True
        t2 = time.time()
        logging.debug('check_pwd took {}'.format(t2 - t))

        if error:
            error_text = "Yo! You gave an invalid username or incorrect password!"
            self.render('login.html', page_title='Log In', user=None, error=error_text)
            self.tf.send({'users.logins.failure': 1}, lambda x: x)
            return
        
        self.set_secure_cookie('user', str(user.id))
        self.tf.send({'users.logins.success': 1}, lambda x: x)
        self.redirect('/')


class RegisterHandler(base.BaseHandler):
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        if user is not None:
            self.redirect('/')
        self.render('register.html', page_title='Register', user=user, error='')

    @web.asynchronous
    def post(self):
        email = self.get_argument('email', '')
        display_name = self.get_argument('display_name', '')
        password = self.get_argument('password', '')
        password_confirm = self.get_argument('password_confirm', '')
        url = self.get_argument('url', '')
        public = True if self.get_argument('public', '') == 'yes' else False

        # check for general errors
        error = False
        if not email or not password or not password_confirm or not url:
            error = True
        if password != password_confirm:
            error = True
        if error:
            error_text = 'Missing a field or passwords do not match, all fields are required.'
            self.render('register.html', page_title='Register', user=None, error=error_text)
            return

        # check that email hasn't already been used
        check_user = models.User.objects(email=email).first()
        if check_user:
            error_text = 'The email you tried already has an account. Please log in or register with a different email address.'
            self.render('register.html', page_title='Register', user=None, error=error_text)
            return
 
        # make sure url is unique
        if url and not models.url_unique(url):
            error_text = 'A unique profile URL is required for public accounts!'
            self.render("register.html", page_title="Register", user=None, error=error_text)

        new_user = models.User(email=email)
        new_user.password = util.hash_pwd(password)
        new_user.display_name = display_name
        new_user.url = url
        new_user.public = public
        new_user.save()

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
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=None)

    @web.authenticated
    @web.asynchronous
    @gen.engine
    def post(self):
        user = self.get_current_user()
        url = self.get_argument('url', '')
        display_name = self.get_argument('displayname', '')
        url = self.get_argument('url', '')
        public = self.get_argument('public', '')

        if not display_name:
            error = 'A display name is required!'
            self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=error)
            return

        public = True if public == 'yes' else False

        error = False
        if url == '':
            error = 'A profile URL is required for public accounts!'
            # make sure url is unique
            if not models.url_unique(url, user):
                error = 'A profile URL is required for public accounts!'
        if error:
            self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=error)
            return

        user.public = public
        user.url = url
        user.display_name = display_name
        user.save()

        yield gen.Task(self.tf.send, {'users.settings.changed': 1})
        self.redirect('/settings')

class DailyMileHandler(base.BaseHandler, auth.OAuth2Mixin):
    _OAUTH_AUTHORIZE_URL = 'https://api.dailymile.com/oauth/authorize'
    _OAUTH_ACCESS_TOKEN_URL = 'https://api.dailymile.com/oauth/token'

    @web.authenticated
    @web.asynchronous
    def get(self):
        redirect_uri=self.application.config['dailymile_redirect']
        client_id=self.application.config['dailymile_client_id']
        client_secret=self.application.config['dailymile_client_secret']


        logging.debug('auth handler') 
        if self.get_argument("code", None):
            logging.debug('after redirect') 
            self.get_authenticated_user(self._on_auth)
            return

        logging.debug('before redirect') 
        extra = {'response_type': 'code'}
        self.authorize_redirect(
                redirect_uri=redirect_uri,
                client_id=client_id,
                client_secret=client_secret,
                extra_params=extra)

    @gen.engine
    def get_authenticated_user(self, callback):
        """Fetches the authenticated dailymile user.
        """
        redirect_uri=self.application.config['dailymile_redirect']
        client_id=self.application.config['dailymile_client_id']
        client_secret=self.application.config['dailymile_client_secret']

        code = self.get_argument("code")
        extra = {
                'grant_type': 'authorization_code',
        }
        url = self._OAUTH_ACCESS_TOKEN_URL
        params = {
                'code': code,
                'redirect_uri': redirect_uri,
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'authorization_code'
        }
        client = httpclient.AsyncHTTPClient()
        response = yield gen.Task(client.fetch, url, method='POST',
                body=urllib.urlencode(params))
        callback(escape.json_decode(response.body))
    
    
    def _on_auth(self, data):
        user = self.get_current_user()
        user.dailymile_token = data['access_token']
        user.export_to_dailymile = True
        user.save()

        crosspost.send_user(self.redis, user)

        # queue past runs for the worker process to cross post
        self.tf.send({'users.dailymile.login': 1}, lambda x: x)
        self.redirect('/settings')

class DailyMileLogoutHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    @gen.engine
    def post(self):
        user = self.get_current_user()
        user.export_to_dailymile = False
        user.dailymile_token = ''
        user.save()

        yield gen.Task(self.tf.send, {'users.dailymile.logout': 1})
        self.redirect('/settings')
