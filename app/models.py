
import mongoengine
import datetime
import dateutil

class User(mongoengine.Document):
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField()

class Run(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    date = mongoengine.DateTimeField(default=datetime.date.today())
    distance = mongoengine.DecimalField()
    time = mongoengine.StringField()
    notes = mongoengine.StringField()

    @classmethod
    def _current_monday(cls):
        delta = dateutil.relativedelta.relativedelta(
                    weekday=dateutil.relativedelta.MO(-1))
        date = datetime.date.today() - delta
        return date

    @classmethod
    def this_week_runs(cls, user):
        return cls.get_runs(user, cls._current_monday())

    @classmethod
    def get_runs(cls, user, date):
        """
        Will return a QuerySet of runs that happened on or after the specified date
        """
        return cls.objects(user=user, date__gte=date)

    @classmethod
    def this_week_mileage(cls, user):
        return cls.get_mileage(user, cls._current_monday())

    @classmethod
    def get_mileage(cls, user, date):
        """
        returns total mileage run on and since date
        """
        runs = cls.get_runs(user, date)
        
        def _accumulate(r1, r2):
            return float(r1) + float(r2.distance)

        return reduce(_accumulate, runs, 0)
