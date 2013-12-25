
import datetime
import logging

import dateutil
import dateutil.parser
import mongoengine
from dateutil.relativedelta import relativedelta
from tornado import escape, gen

import cache


@gen.coroutine
def get_user_by_uid(r, uid):
    user = User.objects(id=uid).first()
    raise gen.Return(user)
    user = yield cache.get(r, uid)
    if user:
        logging.debug('cache hit for {}'.format(uid))
        raise gen.Return(user)
    else:
        logging.debug('cache miss for {}'.format(uid))
        user = User.objects(id=uid).first()
        cache.send(r, user)
        raise gen.Return(user)


@gen.coroutine
def get_user_by_email(r, u):
    user = User.objects(email=u).first()
    raise gen.Return(user)
    user = yield cache.get(r, u)
    if user:
        logging.debug('cache hit for {}'.format(u))
        raise gen.Return(user)
    else:
        logging.debug('cache miss for {}'.format(u))
        user = User.objects(email=u).first()
        cache.send(r, user)
        raise gen.Return(user)


@gen.coroutine
def get_user_by_url(r, u):
    user = User.objects(url=u).first()
    raise gen.Return(user)
    user = yield cache.get(r, u)
    if user:
        logging.debug('cache hit for {}'.format(u))
        raise gen.Return(user)
    else:
        logging.debug('cache miss for {}'.format(u))
        user = User.objects(url=u).first()
        cache.send(r, user)
        raise gen.Return(user)


def url_unique(url, user=None):
    unique = True
    urls = User.objects(url=url)
    if urls.count() > 1:
        unique = False
    elif user:
        if urls.first() and urls.first().email != user.email:
            unique = False
    return unique

def _current_monday():
    delta = dateutil.relativedelta.relativedelta(
                weekday=dateutil.relativedelta.MO(-1))
    date = datetime.date.today() - delta
    return date

def time_to_seconds(time):
    """
    returns time in seconds for strings formatted in the following ways:

    HH:MM:SS
    MM:SS
    MM

    raises ValueError if the string is not formatted like one of those
    """
    seconds = 0

    parts = time.split(':')
    if len(parts) == 3: # hours:minutes:seconds
        seconds += int(parts[0]) * 60 * 60
        seconds += int(parts[1]) * 60
        seconds += int(parts[2])
    elif len(parts) == 2: # minutes:seconds
        seconds += int(parts[0]) * 60
        seconds += int(parts[1])
    elif len(parts) == 1: # minutes
        seconds += int(parts[0]) * 60
    else: # error
        raise ValueError('Time not in correct format')
    return seconds

def seconds_to_time(seconds):
    hours = 0
    minutes = 0
    while seconds > 59:
        seconds -= 60
        minutes += 1
    while minutes > 59:
        minutes -= 60
        hours += 1

    if hours == 0:
        return '{:01}:{:02}'.format(minutes, seconds)
    else:
        return '{}:{:02}:{:02}'.format(hours, minutes, seconds)


def get_this_week_run_data(user):
    this_week_runs = Run.this_week_runs(user)
    return _format_this_week_run_data(this_week_runs)


def get_recent_run_data(user):
    day = datetime.date.today() - dateutil.relativedelta.relativedelta(days=21)
    runs = Run.get_runs(user, date=day)
    return _format_recent_run_data(runs)


def _find_monday(date):
    """
    given a datetime object, return a datetime object of the
    previous monday.

    IE - if date is a monday, return date. If date is a wednesday,
    return the datetime object from 2 days earlier
    """
    while date.weekday() != 0:
        date -= dateutil.relativedelta.relativedelta(days=1)
    return date


def _format_this_week_run_data(given_runs):
    date = _current_monday()
    if given_runs:
        date = _find_monday(given_runs[0].date)
    this_week_runs = [Run(
        date=date+dateutil.relativedelta.relativedelta(days=x),
        distance=0.0)
        for x in range(7)]

    runs = []
    for r in this_week_runs:
        runs.append({'x': r.date.strftime("%c"), 'y': 0.0})

    for r in given_runs:
        # find and add data
        for r2 in runs:
            if r2['x'] == r.date.ctime():
                r2['y'] += float(r.distance)

    data = {
        'xScale': 'ordinal',
        'yScale': 'linear',
        'main': [
            {
                'data': runs
            }
        ]
    }
    return data


def _format_recent_run_data(given_runs):
    date = datetime.date.today()
    this_week_runs = [Run(
        date=date-dateutil.relativedelta.relativedelta(days=x),
        distance=0.0)
        for x in range(21)]

    runs = []
    for r in this_week_runs:
        runs.append({'x': r.date.strftime("%c"), 'y': 0.0})

    for r in given_runs:
        # find and add data
        for r2 in runs:
            if r2['x'] == r.date.ctime():
                r2['y'] += float(r.distance)

    data = {
        'xScale': 'ordinal',
        'yScale': 'linear',
        'main': [
            {
                'data': runs
            }
        ]
    }
    return data


class User(mongoengine.Document):
    display_name = mongoengine.StringField(required=True)
    url = mongoengine.StringField(default="")
    public = mongoengine.BooleanField(required=False)
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField()
    dailymile_token = mongoengine.StringField()
    facebook = mongoengine.DictField(default={})
    export_to_dailymile = mongoengine.BooleanField(default=False)
    streaks = mongoengine.DictField(default=None)
    hashtags = mongoengine.StringField(default="")
    meta = {
        'indexes': ['id', 'url', 'email']
    }

    def save(self, r):
        cache.invalidate(r, self)
        cache.send(r, self)
        return super(User, self).save()

    @property
    def total_mileage(self):
        return Run.get_mileage(self)

    @property
    def yearly_mileage(self):
        year = datetime.date.today().year
        date = dateutil.parser.parse('1-1-{}'.format(year))
        return Run.get_mileage(self, date=date)

    @property
    def uri(self):
        return '/u/{}'.format(self.url)

    def calculate_streaks(self, redis):
        runs = Run.objects(user=self, distance__gt=0).order_by('date')
        self.streaks = self._calculate_streaks(runs)
        self.save(redis)

    @classmethod
    def _calculate_streaks(cls, runs):
        today = datetime.date.today()
        if len(runs) == 0:
            longest = {
                'length': 0,
                'start': '1 step forward',
                'end': '1 step back'
            }
        elif len(runs) == 1 and runs[0].date.strftime("%m/%d/%Y") != today.strftime("%m/%d/%Y"):
            longest = {
                'length': 1,
                'start': runs[len(runs)-1].date.strftime("%m/%d/%Y"),
                'end': runs[len(runs)-1].date.strftime("%m/%d/%Y")
            }
        else:
            current_streak = 1
            current_streak_start = -1
            longest_streak = 1
            longest_streak_start = 0
            for i in range(0, len(runs) - 1):
                delta = relativedelta(runs[i+1].date, runs[i].date)
                if delta.days == 1 and delta.months == 0 and delta.years == 0:
                    if current_streak == 1:
                        current_streak_start = i
                    current_streak += 1
                    if current_streak > longest_streak:
                        longest_streak = current_streak
                        longest_streak_start = current_streak_start
                elif delta.days == 0 and delta.months == 0 and delta.years == 0:
                    continue
                else:
                    current_streak = 1
            longest = {
                'length': longest_streak,
                'start': runs[longest_streak_start].date.strftime("%m/%d/%Y"),
                'end': runs[longest_streak_start+longest_streak-1].date.strftime("%m/%d/%Y"),
            }

        current_streak = 1
        if len(runs) == 0 or relativedelta(runs[len(runs)-1].date, today).days < -1:
            current = {
                'length': 0,
                'start': 'Couch',
                'end': 'Potato Chips'
            }
        else:
            for i in range(len(runs)-1, 0, -1):
                delta = relativedelta(runs[i-1].date, runs[i].date)
                if delta.days == -1 and delta.months == 0 and delta.years == 0:
                    current_streak += 1
                elif delta.days == 0 and delta.months == 0 and delta.years == 0:
                    continue
                else:
                    break
            current = {
                'length': current_streak,
                'start': runs[len(runs)-current_streak].date.strftime(
                    "%m/%d/%Y"),
                'end': runs[len(runs)-1].date.strftime("%m/%d/%Y")
            }

        return {'longest': longest, 'current': current}


class Run(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    date = mongoengine.DateTimeField(default=datetime.date.today())
    distance = mongoengine.FloatField()
    time = mongoengine.IntField()  # store time in seconds for easy manipulation
    notes = mongoengine.StringField()
    exported_to_dailymile = mongoengine.BooleanField(default=False)
    meta = {
        'indexes': [('user', '-date'), ('user', '+date'), 'user']
    }

    @property
    def pace(self):
        if not self.time or not self.distance:
            return 'N/A'
        return seconds_to_time(int(self.time/self.distance)) + ' pace'

    @classmethod
    def this_week_runs(cls, user):
        return cls.get_runs(user, date=_current_monday())

    @classmethod
    def get_recent_runs(cls, user, num_runs):
        return Run.objects(user=user).order_by('-date')[:num_runs]

    @classmethod
    def get_runs(cls, user, date=None, keywords=None):
        """
        Will return a QuerySet of runs that happened on or after the specified date
        """
        if date:
            return cls.objects(user=user, date__gte=date).order_by('date')
        if keywords is not None:
            return cls.objects(user=user, notes__icontains=keywords).order_by('date')
        return cls.objects(user=user).order_by('date')

    @classmethod
    def this_week_mileage(cls, user):
        return cls.get_mileage(user, date=_current_monday())


    @classmethod
    def get_mileage(cls, user, date=None):
        """
        returns total mileage run on and since date
        """
        if date:
            runs = cls.get_runs(user, date=date)
        else:
            runs = cls.get_runs(user)

        def _accumulate(r1, r2):
            return float(r1) + float(r2.distance)

        return reduce(_accumulate, runs, 0)

    @property
    def pretty_time(self):
        return seconds_to_time(self.time)

    @property
    def uri(self):
        return '/u/{}/run/{}'.format(self.user.url, str(self.id))

    @property
    def pretty_notes(self):
        return escape.xhtml_escape(self.notes).replace('\r\n', '<br />')

    @classmethod
    def get_calendar_runs(cls, user, date=None):
        """
        Returns runs in a format that the calendar template can interpret
        for a given user since a given date

        format:

        [
            {'date' :date, runs: [:run1, :run2]},
            {'date' :date2, runs: [:run12, :run22]},
        ]
        """
        date = datetime.datetime(2013, 9, 2)
        def lookahead(day, date, runs, index):
            if index >= len(runs)-1:
                return day

            if date == runs[index+1]:
                day['runs'].append(runs[index+1])
                day = lookahead(day, date, runs, index+1)
            return day

        runs = cls.get_runs(user, date=date)
        result = []
        one_day = relativedelta(days=1)
        previous_date = date - one_day
        next_date = previous_date + one_day
        
        for i in range(len(runs)):
            if runs[i].date <= previous_date:
                continue

            if runs[i].date > next_date:
                # fill in days with 0s when there's no data for them
                while runs[i].date > next_date:
                    day = {
                        'date': next_date,
                        'runs': [Run(date=next_date, distance=0, time=0)],
                    }
                    previous_date += one_day
                    next_date += one_day
                    result.append(day)

            day = {'date': runs[i].date, 'runs': [runs[i]]}
            j = i + 1
            while j < len(runs) and runs[j].date == next_date:
                day['runs'].append(runs[j])
                j += 1
            #day = lookahead(day, previous_date, runs, i)
            previous_date = runs[i].date
            next_date = previous_date + one_day
            result.append(day)

        # if the most recent days don't have runs
        # then fill in with 0s up until today
        today = datetime.datetime.today()
        if runs[len(runs)-1].date != today:
            date = runs[len(runs)-1].date
            while date < today - one_day:
                day = {
                    'date': date + one_day,
                    'runs': [Run(date=next_date, distance=0, time=0)],
                }
                result.append(day)
                date += one_day

        logging.debug(result)
        return result


class Week(mongoengine.Document):
    """
    Stores info about runs for a given week

    - Each Week starts on Monday (stats are aggregated Mon-Sun)
    - Time is stored in Seconds
    - Distance is Miles
    """
    user = mongoengine.ReferenceField(User)
    date = mongoengine.DateTimeField()
    distance = mongoengine.FloatField(default=0)
    time = mongoengine.IntField(default=0) # in seconds

    @property
    def pretty_time(self):
        return seconds_to_time(self.time)

    @classmethod
    def this_week(cls, user):
        monday = _current_monday()
        week = cls.objects(user=user, date=monday).first()
        if not week: # create if it doesn't exist
            week = cls(user=user, date=monday)
            week.save()
        return week


class Group(mongoengine.Document):
    """
    Stores info about a collection of users in a group
    """
    name = mongoengine.StringField(required=True)
    url = mongoengine.StringField(unique=True, required=True)
    admins = mongoengine.ListField(mongoengine.ReferenceField(User))
    members = mongoengine.ListField(mongoengine.ReferenceField(User))
    
    @classmethod
    def all_groups(self):
        return Group.objects()
    
    @classmethod
    def url_exists(self, url):
        group = Group.objects(url=url).first()
        return True if group else False

    @property
    def uri(self):
        return '/g/{}'.format(self.url)


class Race(mongoengine.Document):
    """
    Stores info about a race that a user runs
    """
    user = mongoengine.ReferenceField(User)
    name = mongoengine.StringField(required=True)
    notes = mongoengine.StringField(default='')
    date = mongoengine.DateTimeField(required=True)
    distance = mongoengine.FloatField(default=0)
    distance_units = mongoengine.StringField(default='miles')
    time = mongoengine.IntField(default=0) # in seconds

    @property
    def pretty_notes(self):
        return escape.xhtml_escape(self.notes).replace('\r\n', '<br />')


    @property
    def pretty_time(self):
        return seconds_to_time(self.time)


    @property
    def uri(self):
        return '{}/races/{}'.format(self.user.uri, str(self.id))

