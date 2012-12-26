
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
            logging.debug(date)
            expected_dates.add(date)
            date += dateutil.relativedelta.relativedelta(days=1)
        logging.debug(expected_dates)

        runs = []
        dates = set()
        for r in this_week_runs:
            if r.date not in dates:
                runs.append({'x': r.date.strftime("%x"), 'y': float(r.distance)})
            else:
                # find and add data
                for r2 in runs:
                    if r2['x'] == r.date.strftime("%x"):
                        r2['y'] += float(r.distance)
            dates.add(r.date)

        # for days without runs yet, add 0 mileage
        for d in expected_dates - dates:
            runs.append({'x': d.strftime("%x"), 'y': 0.0})

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

