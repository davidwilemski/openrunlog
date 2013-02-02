
import base
import crosspost
import models
import util
import datetime
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
            self.redirect_msg('/u/%s' % user.url, {'error': msg})
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

        if user.export_to_dailymile:
            crosspost.send_run(self.redis, run)

        self.redirect('/')

class RemoveRunHandler(base.BaseHandler):
    @web.asynchronous
    @web.authenticated
    def post(self):
        run_id = self.get_argument('run_id', '')
        user = self.get_current_user()

        if not run_id:
            self.redirect_msg('/', {'error': 'Could not find run (invalid).'})
            return

        run = models.Run.objects(id=run_id).first()
        if not run:
            self.redirect_msg('/', {'error': 'Could not find run (non-zero).'})
            return

        if run.user.email != user.email:
            self.redirect_msg('/', {'error': 'You do not have permission to delete that run!'})

        # remove this run from the week's aggregate
        monday = run.date - dateutil.relativedelta.relativedelta(days=run.date.weekday())
        week = models.Week.objects(date=monday, user=self.get_current_user()).first()
        if not week:
            # we shouldn't get here - there should be a week for this run
            self.redirect_msg('/', {'error': 'Something went really, really wrong removing the run (weekly totals)'})
            return

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


class ShowRunHandler(base.BaseHandler):
    @web.asynchronous
    def get(self, userurl, run):
        user = self.get_current_user()
        profile = models.User.objects(url=userurl).first()

        if not profile.public and (not user or profile.email != user.email):
            self.render('private.html', page_title='Private Profile', user=user, profile=profile, error=None)

        run = models.Run.objects(id=run).first()
        year = datetime.date.today().year

        self.render('run.html', page_title='{}\' {} mile run'.format(profile.display_name, run.distance), user=user, profile=profile, run=run, error=None, this_year=year)
