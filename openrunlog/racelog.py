
import datetime

import dateutil.parser
from tornado import gen, web

import base
import models


class AllRacesHandler(base.BaseHandler):
    @gen.coroutine
    @web.asynchronous
    @base.authorized
    def get(self, url):
        self.tf.send({'profile.racelog.views': 1}, lambda x: x)
        error = self.get_error()
        year = datetime.date.today().year

        user = yield self.get_current_user_async()
        profile = yield models.get_user_by_url(self.redis, url)
        races = models.Race.objects(user=profile).order_by('-date')

        self.render('races.html', page_title='Racelog', user=user, today=datetime.date.today().strftime("%x"), error=error, this_year=year, profile=profile, races=races)


    @base.authenticated_async
    @web.asynchronous
    @gen.coroutine
    def post(self, url):
        self.tf.send({'profile.racelog.adds': 1}, lambda x: x)

        error = self.get_error()
        year = datetime.date.today().year

        user = yield self.get_current_user_async()
        profile = yield models.get_user_by_url(self.redis, url)

        if user.email != profile.email:
            self.redirect_msg('/', {'error': 'You do not have permission to do add a run for this user.'})
            return

        date = self.get_argument('date', '')
        date = dateutil.parser.parse(date, fuzzy=True)
        name = self.get_argument('name', '')
        distance = self.get_argument('distance', '')
        distance = float(distance)
        distance_units = self.get_argument('distance_units', '')
        time = self.get_argument('time', '')
        pacetime = self.get_argument('pacetime', 'time')
        notes = self.get_argument('notes', '')

        try:
            time = models.time_to_seconds(time) if time != '' else 0
        except ValueError, e:
            msg = "The value you entered for time was not valid. Please enter your time in format HH:MM:SS or MM:SS or MM."
            self.redirect_msg('/u/%s' % user.url, {'error': msg})
            return

        race = models.Race(
                user=user,
                name=name, 
                date=date,
                distance=distance,
                distance_units=distance_units,
                notes=notes,
                time=time)
        race.save()
        self.redirect(user.uri + '/races')


class ShowRaceHandler(base.BaseHandler):
    @web.asynchronous
    @gen.coroutine
    @base.authorized
    def get(self, userurl, raceid):
        user = yield self.get_current_user_async()
        profile = yield models.get_user_by_url(self.redis, userurl)

        race = models.Race.objects(id=raceid).first()

        if race == None:
            # 404
            self.send_error(404)
            return

        year = datetime.date.today().year
        yield gen.Task(self.tf.send, {'profile.races.views': 1})

        title = '{} raced {} - {} {}'.format(profile.display_name, race.name, race.distance, race.distance_units)
        self.render('race.html', page_title=title, user=user, profile=profile, race=race, error=None, this_year=year)
