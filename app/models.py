
import mongoengine
import datetime
import dateutil

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
    return ':'.join((str(hours), str(minutes), str(seconds)))



class User(mongoengine.Document):
    email = mongoengine.EmailField(required=True, unique=True)
    password = mongoengine.StringField()

class Run(mongoengine.Document):
    user = mongoengine.ReferenceField(User)
    date = mongoengine.DateTimeField(default=datetime.date.today())
    distance = mongoengine.FloatField()
    time = mongoengine.IntField() # store time in seconds for easy manipulation
    notes = mongoengine.StringField()

    @classmethod
    def this_week_runs(cls, user):
        return cls.get_runs(user, _current_monday())

    @classmethod
    def get_runs(cls, user, date):
        """
        Will return a QuerySet of runs that happened on or after the specified date
        """
        return cls.objects(user=user, date__gte=date)

    @classmethod
    def this_week_mileage(cls, user):
        return cls.get_mileage(user, _current_monday())

    @classmethod
    def get_mileage(cls, user, date):
        """
        returns total mileage run on and since date
        """
        runs = cls.get_runs(user, date)
        
        def _accumulate(r1, r2):
            return float(r1) + float(r2.distance)

        return reduce(_accumulate, runs, 0)

    @property
    def pretty_time(self):
        return seconds_to_time(self.time)



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

