
import base
import models
import util
import dateutil.parser

from tornado import web

class AddRunHandler(base.BaseHandler):
    @web.asynchronous
    @web.authenticated
    def get(self):
        self.render('add-run.html', page_title='Add A Run', user=self.get_current_user())

    @web.asynchronous
    @web.authenticated
    def post(self):
        date = self.get_argument('date', '')
        date = dateutil.parser.parse(date, fuzzy=True)
        distance = self.get_argument('distance', '')
        time = self.get_argument('time', '')
        notes = self.get_argument('notes', '')
        user = self.get_current_user()

        distance = float(distance)
        if not util.validate_time(time):
            self.finish('error, go back and try again')

        run = models.Run(user=user)
        run.distance = distance
        run.time = time
        run.notes = notes
        run.save() # record the run

        self.redirect('/')
