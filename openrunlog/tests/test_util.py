
import unittest

from openrunlog import util


class BCryptTests(unittest.TestCase):
    def test_bcrypt(self):
        password = 'password'
        self.assertTrue(util.check_pwd(password, util.hash_pwd(password)))
