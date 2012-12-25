
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

        delta = dateutil.relativedelta.relativedelta()
        delta.days = 7
        date = datetime.date.today() - delta
        this_week_runs = models.Run.objects(date__gt=date)

        runs = [ {'x': r.date.strftime("%x"), 'y': float(r.distance)} for r in this_week_runs]

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

