
import datetime

import dateutil.parser
from tornado import concurrent, gen, web

import base
import constants
import models
import rqworkers


class AddRunHandler(base.BaseHandler):
    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def post(self):
        date = self.get_argument('date', '')
        date = dateutil.parser.parse(date, fuzzy=True)
        distance = self.get_argument('distance', '')
        distance = float(distance)
        time = self.get_argument('time', '')
        pacetime = self.get_argument('pacetime', 'time')
        notes = self.get_argument('notes', '')
        user = yield self.get_current_user_async()

        try:
            time = models.time_to_seconds(time) if time != '' else 0
            if pacetime == 'pace':
                time = int(time*distance)
        except ValueError, e:
            msg = "The value you entered for time was not valid. Please enter your time in format HH:MM:SS or MM:SS or MM."
            self.redirect_msg('/u/%s' % user.url, {'error': msg})
            return

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

        rqworkers.calculate_streaks.delay(user)

        yield gen.Task(self.tf.send, {'profile.runs.added': 1})
        self.redirect('/')

class RemoveRunHandler(base.BaseHandler):
    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def post(self):
        run_id = self.get_argument('run_id', '')
        user = yield self.get_current_user_async()

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
        week = models.Week.objects(date=monday, user=user).first()
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

        self.redis.rpush(constants.calculate_streaks, str(user.id))

        yield gen.Task(self.tf.send, {'profile.runs.removed': 1})
        self.redirect('/')


class ShowRunHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    @base.authorized
    def get(self, userurl, run):
        user = yield self.get_current_user_async()
        profile = yield models.get_user_by_url(self.redis, userurl)

        run = models.Run.objects(id=run).first()

        if run is None:
            self.send_error(404)
            return

        year = datetime.date.today().year

        yield gen.Task(self.tf.send, {'profile.runs.views': 1})
        self.render('run.html', page_title='{}\'s {} mile run'.format(profile.display_name, run.distance), user=user, profile=profile, run=run, error=None, this_year=year)


class AllRunsHandler(base.BaseHandler):
    @concurrent.run_on_executor
    def get_runs(self, profile, keywords):
        runs = models.Run.get_runs(
            profile, keywords=keywords).order_by('-date')
        return runs

    @web.asynchronous
    @gen.coroutine
    @base.authorized
    def get(self, userurl):
        user = yield self.get_current_user_async()
        profile = yield models.get_user_by_url(self.redis, userurl)
        keywords = self.get_argument('keywords', None)

        runs = yield self.get_runs(profile, keywords)
        year = datetime.date.today().year
        title = '{}\'s training log'.format(profile.display_name)

        def run_uri(run):
            return '/u/{}/run/{}'.format(profile.url, str(run.id))

        yield gen.Task(self.tf.send, {'profile.allruns.views': 1})

        def render():
            self.render(
                'allruns.html', page_title=title, user=user,
                profile=profile, runs=runs, error=None, this_year=year,
                run_uri=run_uri, keywords=keywords)
        yield self.execute_thread(render)
