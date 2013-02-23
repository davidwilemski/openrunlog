
import datetime
import unittest
from openrunlog import models, data
import json

class MRDi():
    key = None
    value = None

    def __init__(self, k, v):
        self.key = k
        self.value = v

class MonthRuns(unittest.TestCase):
    def test_fill_in_days_with_zero_runs(self):
        runs = []

        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)
        i_date = today - 31 * one_day
        expected_data = []

        while i_date <= today:
            expected_data.append([
                i_date.strftime("%Y-%m-%d"), # date string
                i_date.isocalendar()[1],     # day of week
                0                            # number of runs
            ])
            i_date += one_day
        expected_data = str(expected_data).replace("'", '"')

        returned_data = data.MonthRunsHandler._fill_blank_days(runs)

        self.assertEqual(returned_data, expected_data)
        self.assertEqual(32, len(json.loads(returned_data)))

    def test_fill_in_days_with_one_run(self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)

        # this has to be a map reduce document (kinda)
        runs = [
            MRDi(today-one_day, 1)
        ]

        i_date = today - 31 * one_day
        expected_data = []

        # this loop creates an empty set
        while i_date <= today:
            expected_data.append([
                i_date.strftime("%Y-%m-%d"), # date string
                i_date.isocalendar()[1],     # day of week
                0                            # number of runs
            ])
            i_date += one_day
        # now set the second to last one to have 1 run
        # since that's the one we returned
        expected_data[-2] = [
            (today-one_day).strftime("%Y-%m-%d"), # date string
            (today-one_day).isocalendar()[1],     # day of week
            1                                     # number of runs
        ]

        expected_data = str(expected_data).replace("'", '"')

        returned_data = data.MonthRunsHandler._fill_blank_days(runs)

        self.assertEqual(returned_data, expected_data)
        self.assertEqual(32, len(json.loads(returned_data)))

    def test_fill_in_zero_days_when_all_have_runs(self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)

        # this has to be a map reduce document (kinda)
        i_date = today - 31 * one_day
        runs = []
        while i_date <= today:
            runs.append(MRDi(i_date, 1))
            i_date += one_day

        i_date = today - 31 * one_day
        expected_data = []

        # this loop creates an empty set
        while i_date <= today:
            expected_data.append([
                i_date.strftime("%Y-%m-%d"), # date string
                i_date.isocalendar()[1],     # day of week
                1                            # number of runs
            ])
            i_date += one_day

        expected_data = str(expected_data).replace("'", '"')

        returned_data = data.MonthRunsHandler._fill_blank_days(runs)

        self.assertEqual(returned_data, expected_data)
        self.assertEqual(32, len(json.loads(returned_data)))

    def test_fill_in_zero_days_when_all_have_different_number_of_runs(self):
        today = datetime.date.today()
        one_day = datetime.timedelta(days=1)

        # this has to be a map reduce document (kinda)
        i_date = today - 31 * one_day
        i = 1
        runs = []
        while i_date <= today:
            runs.append(MRDi(i_date, i))
            i_date += one_day
            i += 1

        i_date = today - 31 * one_day
        i = 1
        expected_data = []

        # this loop creates an empty set
        while i_date <= today:
            expected_data.append([
                i_date.strftime("%Y-%m-%d"), # date string
                i_date.isocalendar()[1],     # day of week
                i                            # number of runs
            ])
            i_date += one_day
            i += 1

        expected_data = str(expected_data).replace("'", '"')

        returned_data = data.MonthRunsHandler._fill_blank_days(runs)

        self.assertEqual(returned_data, expected_data)
        self.assertEqual(32, len(json.loads(returned_data)))
