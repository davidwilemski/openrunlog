
import unittest

from openrunlog import models, util


fbid = '1264253926'
email = 'dtwwtd@gmail.com'

class BCryptTests(unittest.TestCase):
    def test_bcrypt(self):
        password = 'password'
        self.assertTrue(util.check_pwd(password, util.hash_pwd(password)))


class ImageHTMLTests(unittest.TestCase):
    expected_fb_url = 'https://graph.facebook.com/1264253926/picture?type=small'
    expected_robo_url = 'https://robohash.org/dtwwtd@gmail.com.jpg?gravatar=yes&size=50x50'
    expected_bigrobo_url = 'https://robohash.org/dtwwtd@gmail.com.jpg?gravatar=yes&size=180x180'

    def test_fb_image_url(self):
        url = util.fb_image_url(fbid)
        self.assertEqual(url, self.expected_fb_url)

    def test_robohash_img_url(self):
        url = util.robohash_image_url(email, 50)
        self.assertEqual(url, self.expected_robo_url)

    def test_image_html(self):
        expected_base_html = '<img src="{}" />'
        expected_fb_html = expected_base_html.format(self.expected_fb_url)
        expected_robo_html = expected_base_html.format(self.expected_robo_url)
        expected_bigrobo_html = expected_base_html.format(self.expected_bigrobo_url)

        fbuser = models.User(display_name='david', email=email)
        fbuser.facebook['id'] = fbid
        robouser = models.User(display_name='david', email=email)

        fb_html = util.image_html(fbuser, 'small')
        robo_html = util.image_html(robouser, 'small')
        bigrobo_html = util.image_html(robouser, 'big')

        self.assertEqual(expected_fb_html, fb_html)
        self.assertEqual(expected_robo_html, robo_html)
        self.assertEqual(expected_bigrobo_html, bigrobo_html)
