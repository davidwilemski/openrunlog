
from tornado import web

import base
import models
import util

class LoginHandler(base.BaseHandler):
    @web.asynchronous
    def get(self):
        if self.get_current_user() is not None:
            self.redirect('/')
        self.render('login.html', page_title='Log In', user=None)

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

        if user and not util.check_pwd(password, user.password):
            error = True

        error_text = ''
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
        self.render('register.html', page_title='Register', user=user)

    @web.asynchronous
    def post(self):
        email = self.get_argument('email', '')
        password = self.get_argument('password', '')
        password_confirm = self.get_argument('password_confirm', '')

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
                    user=user, 
                    error=error_text)
            return

        # check that email hasn't already been used
        user = models.User.objects(email=email).first()
        if user:
            error_text = 'Please try again.'
            self.render(
                    'register.html', 
                    page_title='Register', 
                    user=user, 
                    error=error_text)
            return

        user = models.User(email=email)
        user.password = util.hash_pwd(password)
        user.save()

        self.set_secure_cookie('user', str(user.id))
        self.redirect('/')


class LogoutHandler(base.BaseHandler):
    @web.asynchronous
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')
