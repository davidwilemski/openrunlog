import requests


class ORLClient(object):
    baseurl = 'https://openrunlog.org/api'

    def __init__(self, user_url, api_key, url=None):
        self.user_url = user_url
        self.api_key = api_key

        if url is not None:
            self.baseurl = url

    def __repr__(self):
        return "{}('{}', '{}', url='{}')".format(
            self.__class__.__name__, self.user_url, self.api_key, self.baseurl)

    def add_run(self, params):
        """
        params is a dict of components of a run:
          - date (str)
          - distance (float) (in miles)
          - time (str) hh::mm:ss or mm:ss
          - pace (str) mm:ss
          - notes (str)

        Only one of time or pace should be sent
        """
        headers = {'api_key': self.api_key}
        url = '{}/runs/{}'.format(self.baseurl, self.user_url)
        return requests.post(url, headers=headers, data=params)
