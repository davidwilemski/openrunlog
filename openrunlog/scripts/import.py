import csv
import env
import dateutil
import dateutil.parser
import mongoengine
from openrunlog import models

def import_csv(filename, email):
    """
    assumes index positions:
    0: date
    1: distance
    2: time
    4: comments
    """
    user = models.User.objects(email=email).first()
    if not user:
        print 'user does not exist'
        return

    with open(filename) as logfile:
        logreader = csv.reader(logfile)
        logreader.next() # skip past field names
        rownum = 0
        for row in logreader:
            # parse data
            try:
                date = dateutil.parser.parse(row[0], fuzzy=True)
            except ValueError:
                print rownum, 'badly formatted date', row[0]
                continue

            if date == dateutil.parser.parse('12/27/12'):
                print rownum

            distance = row[1]
            if not distance:
                distance = 0
            else:
                distance = float(distance)

            time = row[2]
            try:
                if time:
                    time = models.time_to_seconds(time)
                else:
                    time = 0
            except ValueError, e:
                print rownum, 'badly formatted time', time

            notes = row[4]

            # add run to db
            run = models.Run(user=user)
            run.distance = distance
            run.time = time
            run.notes = notes
            run.date = date
            run.validate()
            #print run.date, run.distance, run.time
            run.save()

            # aggregate week data
            monday = date - dateutil.relativedelta.relativedelta(days=date.weekday())
            week = models.Week.objects(date=monday, user=user).first()
            if not week:
                week = models.Week(date=monday, user=user)
            week.time += run.time
            week.distance += run.distance
            week.validate()
            #print week.date, week.distance, week.time
            week.save()

            rownum += 1
 

if __name__ == '__main__':
    config = env.prefix('ORL_')
    mongoengine.connect(
            config['db_name'], 
            host=config['db_uri'])
    import_csv('log.csv', 'dtwwtd@gmail.com')
