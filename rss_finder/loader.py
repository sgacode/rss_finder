import copy

import requests

from . import exceptions


class Loader:
    requests_options_default = {
        'allow_redirects': True,
        'timeout': (30, 30),
        'headers': {},
        'verify': False,
    }

    def __init__(self, requests_options=None):
        self.requests_options = copy.deepcopy(self.requests_options_default)
        if requests_options and isinstance(requests_options, dict):
            self.requests_options.update(requests_options)

    def fetch(self, url: str) -> requests.Response:
        try:
            return requests.get(url, params=self.requests_options)
        except (requests.RequestException, ConnectionError, UnicodeDecodeError) as e:
            raise exceptions.RequestException('Error load url "{0}"'.format(url)) from e
