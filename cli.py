import sys
import logging
import json

from rss_finder.finder import RssFinder
from rss_finder import LOGGER_NAME


if len(sys.argv) < 2:
    raise Exception('Url param is required. Usage: python cli.py {url}')

logger = logging.getLogger(LOGGER_NAME)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)

finder = RssFinder()
res = finder.search(sys.argv[1])
print(json.dumps(res))
