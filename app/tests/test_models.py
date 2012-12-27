
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
        self.assertTrue(models.seconds_to_time(300) == '00:05:00')


if __name__ == '__main__':
    unittest.main()
