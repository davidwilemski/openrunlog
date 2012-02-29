
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

        if not util.check_pwd(password, user.password):
            error = True

        if error:
            self.write('invalid username or password incorrect<br />') 
            self.write('Plase <a href="/login">try again.</a>')
            self.finish()
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
            self.write('Missing a field or passwords do not match, all fields are required.<br />')
            self.write('Plase <a href="/register">try again.</a>')
            self.finish()
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
