
import datetime
import dateutil
from tornado import web, escape

import base
import models
import util

class ThisWeekHandler(base.BaseHandler):
    @web.authenticated
    @web.asynchronous
    def get(self):
        user = self.get_current_user()

        delta = dateutil.relativedelta.relativedelta(
                weekday=dateutil.relativedelta.MO(-1))
        date = datetime.date.today() - delta
        this_week_runs = models.Run.objects(date__gte=date)

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

        data = {
                'xScale': 'ordinal',
                'yScale': 'linear',
                'main': [
                    {
                        'data': runs
                    }
                ]
        }

        self.set_header('Content-Type', 'application/json')
        self.write(escape.json_encode(data))
        self.finish()

