#!/usr/bin/python
# -*- coding: utf-8 -*-


def remove_trailing_junk(url):
    # remove trailing string after parameters
    # e.g. http://www.ics.uci.edu?p=2&c=igb-misc/degrees/index/... ->  http://www.ics.uci.edu?p=2&c=igb-misc
    # http://www.ics.uci.edu/computing/linux/shell.php/computing/account/ ->  http://www.ics.uci.edu/computing/linux/shell.php
    sub_names = ['?', '.htm', '.html', '.php', '.jsp']
    for sub_name in sub_names:
        if sub_name in url and '/' in url[url.index(sub_name):]:
            return url[:
                url.index(sub_name) +
                url[url.index(sub_name):].index('/')
            ]
    return url


def merge_path(parent_path, href):
    parent_dirs = [d for d in parent_path.split('/') if d]
    children_dirs = [c for c in href.split('/') if c]
    total_dirs = parent_dirs + children_dirs
    parsed_dirs = []
    for d in total_dirs:
        if d == '..' and parsed_dirs:
            parsed_dirs = parsed_dirs[:-1]
        elif d != '..':
            parsed_dirs.append(d)
    return '/' + '/'.join(parsed_dirs)