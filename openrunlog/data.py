
import datetime
import dateutil
import functools
import futures
import logging
from tornado import web, escape, gen
from tornado.ioloop import IOLoop

import base
import models
import util

class ThisWeekHandler(base.BaseHandler):
    @web.asynchronous
    def get(self, uid):
        user = self.get_current_user()
        data_user = models.User.objects(id=uid).first()
        if not data_user.public and (not user or user.email != data_user.email):
            self.write_error(403)
            return
        date = models._current_monday()
        this_week_runs = models.Run.this_week_runs(data_user)

        expected_dates = set()
        for x in range(7):
            expected_dates.add(date)
            date += dateutil.relativedelta.relativedelta(days=1)

        runs = []
        dates = set()
        for r in this_week_runs:
            if r.date not in dates:
                runs.append({'x': r.date.strftime("%c"), 'y': r.distance})
            else:
                # find and add data
                for r2 in runs:
                    if r2['x'] == r.date.strftime("%c"):
                        r2['y'] += float(r.distance)
            dates.add(r.date)

        # for days without runs yet, add 0 mileage
        for d in expected_dates - dates:
            runs.append({'x': d.strftime("%c"), 'y': 0.0})

        data = {
                'xScale': 'ordinal',
                'yScale': 'linear',
                'main': [
                    {
                        'data': runs
                    }
                ]
        }

        self.finish(data)


class WeeklyMileageHandler(base.BaseHandler):
    @web.asynchronous
    def get(self, uid):
        user = self.get_current_user()
        since = self.get_argument('since', '')
        window_weeks = self.get_argument('window_weeks', '')

        data_user = models.User.objects(id=uid).first()
        if not data_user.public and (not user or user.email != data_user.email):
            self.write_error(403)
            return

        if window_weeks:
            window_weeks = dateutil.relativedelta.relativedelta(weeks=int(window_weeks))

        try:
            since = int(since)
        except ValueError:
            since = None

        if since:
            since = datetime.date(since, 1, 1)
            weeks = models.Week.objects(user=data_user, date__gte=since)
        else:
            if window_weeks:
                weeks = models.Week.objects(user=data_user, date__gte=datetime.date.today() - window_weeks)
            else:
                weeks = models.Week.objects(user=data_user)

        weeks = [week for week in weeks]

        weeks = sorted(weeks, key=lambda w: w.date)
        last_date = weeks[0].date
        offset = dateutil.relativedelta.relativedelta(days=7)
        for x in range(1, len(weeks)):
            if last_date + offset != weeks[x].date:
                while last_date + offset != weeks[x].date:
                    w = models.Week(distance=0, time=0, date=last_date+offset)
                    weeks.append(w)
                    last_date += offset
            last_date += offset
        weeks = sorted(weeks, key=lambda w: w.date)

        # handle the beginning of the year
        year = datetime.date.today().year
        if since and weeks[0].date != datetime.date(year, 1, 1):
            # manually build a partial week
            runs = models.Run.objects(user=data_user, date__lt=weeks[0].date, date__gte=datetime.date(year, 1, 1))
            week = models.Week(user=data_user)
            week.date = datetime.date(year, 1, 1)
            for run in runs:
                week.distance += run.distance
                week.time += run.time
            weeks.insert(0, week)


        weeks = [ {'x': w.date.strftime('%m-%d-%Y'), 'y': w.distance} for w in weeks]

        # if the user only has 1 week display the last week too
        if len(weeks) == 1:
            last_monday = dateutil.parser.parse(weeks[0]['x']) - dateutil.relativedelta.relativedelta(days=7)
            weeks.append({'x': last_monday.strftime('%m-%d-%Y'), 'y': 0})

        data = {
                'xScale': 'time',
                'yScale': 'linear',
                'main': [
                    {
                        'data': weeks
                    }
                ]
        }

        # 0 fill some data if there is none so that the graph shows
        if since and not weeks:
            weeks.append({'x': since.strftime('%x'), 'y':0})
            weeks.append({'x': (since + dateutil.relativedelta.relativedelta(days=7)).strftime('%m-%d-%Y'), 'y':0})
            data['yMin'] = 0
            data['yMax'] = 100

        self.finish(data)

class WeekdayRunsHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self, uid):
        data_user = models.User.objects(id=uid).first()

        def runs_by_day(user):
            run_map = '''
                function() {
                    // remember, we need 0 to be Monday, so let's adjust
                    //var day = this.date.getDay() - 1;
                    //if(day < 0) { day = 6; }
                    emit(this.date.getDay(), 1);
                };
            '''
            run_reduce = '''
                function(day, counts) {
                    return Array.sum(counts);
                };
            '''

            runs = models.Run.objects(user=user)
            mrd = runs.map_reduce(run_map, run_reduce, 'inline')
            return mrd


        map_reduce_document = (yield gen.Task(
            self.execute_thread, runs_by_day, data_user)).result()


        runs_per_weekday = [0] * 7
        for i in map_reduce_document: 
            runs_per_weekday[int(i.key)] = int(i.value)

        """
        data = {
            'xScale': 'ordinal',
            'yScale': 'linear',
            'yMin': 0,
            'main': [
                { 'data': [{'x':i, 'y':runs_per_weekday[i]} for i in range(len(runs_per_weekday))]}
            ]
        }
        """
        data = { 'data': 
                [
                    {'x':i, 'y':runs_per_weekday[i]} for i in range(
                        len(runs_per_weekday))]}

        self.finish(data)

class DailyRunsHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self, uid):
        user = models.User.objects(id=uid).first()
        
        def runs_per_day(user):
            plus_one_day = datetime.timedelta(days=1)
            today = datetime.date.today()
            if today.month == 2 and today.day == 29:
                d = datetime.date(today.year-1, today.month, today.day-1)
            else:
                d = datetime.date(today.year-1, today.month, today.day)
            runs = models.Run.objects(user=user,date__gt=d)
            data = {str(r.date).split(' ')[0]: [r.date.isocalendar()[1], 1] for r in runs}
            while d <= today:
                if str(d) not in data.keys():
                    data[str(d)] = [d.isocalendar()[1], 0]
                d += plus_one_day
            ret_data = [[k, v[0], v[1]] for k,v in data.iteritems()]
            ret_data = sorted(ret_data, key=lambda i: i[0])
            return ret_data

        runs = (yield gen.Task(
            self.execute_thread, runs_per_day, user)).result()

        self.finish(str(runs).replace("'", '"'))

class MonthRunsHandler(base.BaseHandler):
    @web.asynchronous
    @gen.engine
    def get(self, uid):
        user = models.User.objects(id=uid).first()
        
        def runs_in_month(user):
            plus_one_day = datetime.timedelta(days=1)
            today = datetime.date.today()
            d = today - (31 * plus_one_day)
            runs = models.Run.objects(user=user,date__gt=d)
            data = {str(r.date).split(' ')[0]: [r.date.isocalendar()[1], 1] for r in runs}
            while d <= today:
                if str(d) not in data.keys():
                    data[str(d)] = [d.isocalendar()[1], 0]
                d += plus_one_day
            ret_data = [[k, v[0], v[1]] for k,v in data.iteritems()]
            ret_data = sorted(ret_data, key=lambda i: i[0])
            return ret_data

        runs = (yield gen.Task(
            self.execute_thread, runs_in_month, user)).result()

        self.finish(str(runs).replace("'", '"'))

