import sys

from rss_finder.finder import RssFinder

if len(sys.argv) < 2:
    raise Exception('Url param is required. Usage: python cli.py {url}')

finder = RssFinder()
res = finder.search(sys.argv[1])
print(res)
