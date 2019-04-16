RSS feed finder
===========================

Overview
---------
Finds RSS feed URLS for a given url.

Features
-----
1. Search rss urls based on <link> tag
2. Search rss urls based on <a> tag (href attribute contains rss labels)
3. Check standard rss urls for multiple CMS

Installation
-----
Install via pip:
```bash 
pip install -U git+https://github.com/sgacode/rss_finder#egg=rss_finder
```

Usage
-----
Cli mode:
```bash
python3 cli.py https://www.rbc.ru/
```

Usage in code:\
```python
from rss_finder.finder import RssFinder
finder = RssFinder()
res = finder.search('aif.ru')
```
