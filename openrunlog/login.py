
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
            return
        
        self.set_secure_cookie('user', str(user.id))
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
        public = self.get_argument('public', '')

        error = False
        if not email or not password or not password_confirm:
            error = True

        if password != password_confirm:
            error = True

        if error == True:
            error_text = 'Missing a field or passwords do not match, all fields are required.'
            self.render(
                    'register.html', 
                    page_title='Register', 
                    user=None,
                    error=error_text)
            return

        # check that email hasn't already been used
        user = models.User.objects(email=email).first()
        if user:
            error_text = 'The email you tried already has an account. Please log in or register with a different email address.'
            self.render(
                    'register.html', 
                    page_title='Register', 
                    user=user, 
                    error=error_text)
            return
 
        error = False
        public = True if public == 'yes' else False
        if public and not url:
            error = 'A profile URL is required for public accounts!'
        # make sure url is unique
        if not models.url_unique(url, user):
            error = 'A profile URL is required for public accounts!'
        if error:
            self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=error)
            return

        user = models.User(email=email)
        user.display_name = display_name
        user.password = util.hash_pwd(password)
        user.url = url
        user.public = public
        user.save()

        self.set_secure_cookie('user', str(user.id))
        self.redirect('/')


class LogoutHandler(base.BaseHandler):
    @web.asynchronous
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')

class SettingsHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=None)

    @web.authenticated
    @web.asynchronous
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

        if public == 'yes':
            public = True
            if not url:
                error = 'A profile URL is required for public accounts!'
                self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=error)
                return

            user.public = True
            user.url = url
        else:
            public = False
            user.public = False
            user.url = ''

        # make sure url is unique
        if public and not models.url_unique(url, user):
            error = 'A profile URL is required for public accounts!'
            self.render("settings.html", page_title="Settings for {}".format(user.display_name), user=user, error=error)
            return


        user.display_name = display_name
        user.save()

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
                redirect_uri=self.redirect_uri,
                client_id=self.client_id,
                client_secret=self.client_secret,
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
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
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
        self.redirect('/settings')

class DailyMileLogoutHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def post(self):
        user = self.get_current_user()
        user.export_to_dailymile = False
        user.dailymile_token = ''
        user.save()

        self.redirect('/settings')
