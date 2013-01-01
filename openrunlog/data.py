
import datetime
import dateutil
import logging
from tornado import web, escape

import base
import models
import util

class ThisWeekHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        date = models._current_monday()
        this_week_runs = models.Run.this_week_runs(user)

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
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()
        since = self.get_argument('since', '')
        try:
            since = int(since)
        except ValueError:
            since = None

        if since:
            since = datetime.date(since, 1, 1)
            weeks = models.Week.objects(user=user, date__gte=since)
        else:
            weeks = models.Week.objects(user=user)

        weeks = [ {'x': w.date.strftime('%x'), 'y': w.distance} for w in weeks]

        # if the user only has 1 week display the last week too
        if len(weeks) == 1:
            last_monday = dateutil.parser.parse(weeks[0]['x']) - dateutil.relativedelta.relativedelta(days=7)
            weeks.append({'x': last_monday.strftime('%x'), 'y': 0})


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
            weeks.append({'x': (since + dateutil.relativedelta.relativedelta(days=7)).strftime('%x'), 'y':0})
            data['yMin'] = 0
            data['yMax'] = 100

        self.finish(data)

