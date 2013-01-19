
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

class RemoveRunHandler(base.BaseHandler):
    @web.asynchronous
    @web.authenticated
    def post(self):
        run_id = self.get_argument('run_id', '')
        if run_id == '': return self.redirect('/')
        run = models.Run.objects(id=run_id).get()
        if not run: return self.finish('error. run not found')

        # remove this run from the week's aggregate
        monday = run.date - dateutil.relativedelta.relativedelta(days=run.date.weekday())
        week = models.Week.objects(date=monday, user=self.get_current_user()).first()
        if not week:
            # we shouldn't get here - there should be a week for this run
            self.finish('error, something went really, really wrong removing the run')
        week.time -= run.time
        week.distance -= run.distance
        if week.time == 0 and week.distance == 0:
            # there is no more data for this week, delete it
            week.delete()
        else:
            # there still is week data, save it
            week.save()

        # remove the run itself, always
        run.delete()

        self.redirect('/')
