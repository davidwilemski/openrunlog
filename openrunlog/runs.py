
import base
import models
import util
import dateutil.parser

from tornado import web

class AddRunHandler(base.BaseHandler):
    @web.asynchronous
    @web.authenticated
    def post(self):
        date = self.get_argument('date', '')
        date = dateutil.parser.parse(date, fuzzy=True)
        distance = self.get_argument('distance', '')
        time = self.get_argument('time', '0')
        try:
            time = models.time_to_seconds(time)
        except ValueError, e:
            msg = "The value you entered for time was not valid. Please enter your time in format HH:MM:SS or MM:SS or MM."
            self.redirect_msg('/dashboard', {'error': msg})
            return
        notes = self.get_argument('notes', '')
        user = self.get_current_user()

        distance = float(distance)
        if not util.validate_time(time):
            self.finish('error, go back and try again')

        run = models.Run(user=user)
        run.distance = distance
        run.time = time
        run.notes = notes
        run.date = date
        run.save() # record the run

        # add info to week aggregate
        monday = date - dateutil.relativedelta.relativedelta(days=date.weekday())
        week = models.Week.objects(date=monday, user=user).first()
        if not week:
            week = models.Week(date=monday, user=user)
        week.time += run.time
        week.distance += run.distance
        week.save()

        self.redirect('/')
