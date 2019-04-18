import typing
import logging

import feedparser
import urltools
from lxml.html import fromstring
from lxml import etree

from . import exceptions
from .loader import Loader
from . import LOGGER_NAME


def log(url, msg, level=logging.DEBUG):
    msg = '[{0}] {1}'.format(url, msg)
    logging.getLogger(LOGGER_NAME).log(level, msg)


class RssFinder:

    rss_mime = [
        'application/rss+xml',
        'application/atom+xml',
        'application/rdf+xml',
        'application/rss',
        'application/atom',
        'text/rss+xml',
        'text/atom+xml',
        'text/rss',
        'text/atom',
    ]

    rss_url_labels = ['rss', 'feed']

    typical_urls = [
        'feed', 'wp-rss2.php', '?feed=rss2',  # wordpress
        'rss.xml', 'rss',  # drupal, modx
        '?format=feed&type=rss',  # joomla
        'bitrix/rss.php',  # bitrix
        # custom
        'export/rss.xml',
        'feed/rss/',
        'rss.php',
        'rss/all',
        'rss/all.php',
        'rss/index.xml',
        'rss/index.php',
        'rss/news.xml',
        'rss/news',
        'rss/rss.xml',
        'rss/rss.php',
        'news/rss',
        'news.rss',
        'xml/rss.xml',
    ]

    def __init__(self, requests_options=None, loader_timeout=None):
        self.loader = Loader(requests_options, timeout=loader_timeout)

    def search(self, url: str, max_results=None) -> typing.List[str]:
        url = self.normalize_url(url)
        log(url, 'Start process url')

        # fetch url content
        try:
            r = self.loader.fetch(url)
        except exceptions.RequestException as e:
            log(str(e), url, level=logging.ERROR)
            return []

        log(url, 'Content loaded')

        # try parse from html & validate urls
        log(url, 'Start parse from html')
        res = self.parse_from_html(r.text, url)
        res = [self.normalize_url(res_url, main_url=url) for res_url in res]
        res = [url for url in res if self.validate_rss_url(url)]
        if res and (not max_results or len(res) >= max_results):
            log(url, 'End parse from html => finish, results count: {0}'.format(len(res)))
            return res
        log(url, 'End parse from html, results count: {0}'.format(len(res)))

        # try load common urls
        log(url, 'Start load common urls')
        for cur_url in self.typical_urls:
            cur_url = self.normalize_url('/' + cur_url, main_url=url)
            log(url, 'Try common url {0}'.format(cur_url))

            if self.validate_rss_url(cur_url):
                res.append(cur_url)

            if max_results and len(res) >= max_results:
                break
        log(url, 'End load common urls, results count: {0}'.format(len(res)))

        res = list(set(res))

        log(url, 'End process url, total unique results count: {0}'.format(len(res)))

        return res

    def parse_from_html(self, content: str, url: str) -> typing.List[str]:
        res = []

        # create DOM
        try:
            dom = fromstring(content)
        except (etree.Error, ValueError) as e:
            raise exceptions.ParseException('Error parse content, url "{0}"'.format(url)) from e

        # parse <link> tags
        for mime in self.rss_mime:
            for link_tag in dom.xpath('.//link[@type="{0}"]'.format(mime)):
                res.append(link_tag.attrib['href'])
        if res:
            return res

        # parse links from <a>
        contains_xpath = ' or '.join(
            ['contains(@href, "{0}")'.format(label) for label in self.rss_url_labels]
        )
        for link_tag in dom.xpath('.//a[{0}]'.format(contains_xpath)):
            res.append(link_tag.attrib['href'])

        return res

    def validate_rss_url(self, url: str) -> bool:
        try:
            r = self.loader.fetch(url)
        except exceptions.RequestException as e:
            log(str(e), url, level=logging.ERROR)
            return False

        if r.status_code != 200 or not len(r.text):
            return False

        f = feedparser.parse(r.text)
        if not len(f.entries):
            return False
        return True

    def normalize_url(self, url: str, main_url: str=None) -> str:
        parse_res = dict(urltools.extract(url)._asdict())

        if not parse_res['scheme']:
            parse_res['scheme'] = 'http'

        if not parse_res['domain'] and main_url:
            main_url_parse_res = urltools.extract(main_url)
            parse_res['domain'] = main_url_parse_res.domain
            parse_res['tld'] = main_url_parse_res.tld
            parse_res['subdomain'] = main_url_parse_res.subdomain

        return urltools.construct(
            urltools.URL(
                **parse_res,
            )
        )


