
import datetime
import unittest
from openrunlog import models


class TimeTests(unittest.TestCase):
    def test_valid_time_to_seconds(self):
        self.assertTrue(models.time_to_seconds('1:23:00') == 4980)
        self.assertTrue(models.time_to_seconds('83:00') == 4980)
        self.assertTrue(models.time_to_seconds('83') == 4980)

    def test_invalid_time_to_seconds(self):
        self.assertRaises(ValueError, models.time_to_seconds, 'x83')
        self.assertRaises(ValueError, models.time_to_seconds, 'xlksdjf')
        self.assertRaises(ValueError, models.time_to_seconds, '1:1:23:00')

    def test_valid_seconds_to_time(self):
        self.assertTrue(models.seconds_to_time(4980) == '1:23:00')
        self.assertTrue(models.seconds_to_time(300) == '5:00')
        self.assertTrue(models.seconds_to_time(600) == '10:00')


class StreakTests(unittest.TestCase):
    def test_multiday_streak_longest(self):
        runs = [
            models.Run(date=datetime.datetime(2013, 2, 1, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 2, 2, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 2, 3, 0, 0), distance=4),
        ]

        streaks = models.User._calculate_streaks(runs)

        expected_streaks = {
            'longest': {
                'length': 3,
                'start': datetime.datetime(2013, 2, 1, 0, 0).strftime(
                    "%m/%d/%Y"),
                'end': datetime.datetime(2013, 2, 3, 0, 0).strftime(
                    "%m/%d/%Y")
            },
            'current': {'end': 'Potato Chips', 'length': 0, 'start': 'Couch'}
        }

        self.assertEqual(streaks, expected_streaks)

    def test_multiday_streak_longest_and_current(self):
        today = datetime.date.today()
        d2 = datetime.date(today.year, today.month, today.day-1)
        d3 = datetime.date(today.year, today.month, today.day-2)
        runs = [
            models.Run(date=d3, distance=4),
            models.Run(date=d2, distance=4),
            models.Run(date=today, distance=4),
        ]

        streaks = models.User._calculate_streaks(runs)

        expected_streaks = {
            'longest': {
                'length': 3,
                'start': d3.strftime(
                    "%m/%d/%Y"),
                'end': today.strftime(
                    "%m/%d/%Y")
            },
            'current': {
                'length': 3,
                'start': d3.strftime(
                    "%m/%d/%Y"),
                'end': today.strftime(
                    "%m/%d/%Y")
            },
        }

        self.assertEqual(streaks, expected_streaks)

    def test_multiple_streaks_find_longest_with_current(self):
        today = datetime.date.today()
        runs = [
            models.Run(date=datetime.datetime(2012, 12, 3, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 1, 1, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 1, 2, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 1, 3, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 2, 2, 0, 0), distance=4),
            models.Run(date=datetime.datetime(2013, 2, 3, 0, 0), distance=4),
            models.Run(date=today, distance=4)
        ]

        streaks = models.User._calculate_streaks(runs)

        expected_streaks = {
            'longest': {
                'length': 3,
                'start': datetime.datetime(2013, 1, 1, 0, 0).strftime(
                    "%m/%d/%Y"),
                'end': datetime.datetime(2013, 1, 3, 0, 0).strftime(
                    "%m/%d/%Y")
            },
            'current': {
                'length': 1,
                'start': today.strftime(
                    "%m/%d/%Y"),
                'end': today.strftime(
                    "%m/%d/%Y")
            }
        }

        self.assertEqual(streaks, expected_streaks)

    def test_single_day_streak_longest_and_current(self):
        today = datetime.date.today()
        runs = [
            models.Run(date=today, distance=4)
        ]

        streaks = models.User._calculate_streaks(runs)

        expected_streaks = {
            'current': {
                'length': 1,
                'start': today.strftime(
                    "%m/%d/%Y"),
                'end': today.strftime(
                    "%m/%d/%Y")
            },
            'longest': {
                'length': 1,
                'start': today.strftime(
                    "%m/%d/%Y"),
                'end': today.strftime(
                    "%m/%d/%Y")
            }
        }

        self.assertEqual(streaks, expected_streaks)
    
    def test_streaks_no_runs(self):
        runs = []
        streaks = models.User._calculate_streaks(runs)
        
        expected_streaks = {
            'current': {
                'length': 0,
                'start': 'Couch',
                'end': 'Potato Chips'
            },
            'longest': {
                'length': 0,
                'start': '1 step forward',
                'end': '1 step back'
            }
        }

        self.assertEqual(streaks, expected_streaks)

if __name__ == '__main__':
    unittest.main()
