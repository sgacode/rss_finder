import typing

import feedparser
import urltools
from lxml.html import fromstring
from lxml import etree

from . import exceptions
from .loader import Loader


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

    def __init__(self, requests_options=None):
        self.loader = Loader(requests_options)

    def search(self, url: str, max_results=None) -> typing.List[str]:
        url = self.normalize_url(url)

        # fetch url content
        r = self.loader.fetch(url)

        # try parse from html & validate urls
        res = self.parse_from_html(r.text, url)
        res = [self.normalize_url(res_url, main_url=url) for res_url in res]
        res = [url for url in res if self.validate_rss_url(url)]
        if res and (not max_results or len(res) >= max_results):
            return res

        # try load common urls
        for cur_url in self.typical_urls:
            cur_url = self.normalize_url('/' + cur_url, main_url=url)
            r = self.loader.fetch(cur_url)
            if r.status_code != 200 or not len(r.text):
                continue

            if self.validate_rss_url(cur_url):
                res.append(cur_url)

            if max_results and len(res) >= max_results:
                break

        return list(set(res))

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
        r = self.loader.fetch(url)
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


