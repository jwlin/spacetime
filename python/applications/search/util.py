#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import os
from urlparse import urlparse, parse_qs
from shutil import copyfile


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


def is_not_trap(url, trapCheckTable={}):
    value = set(parse_qs(urlparse(url).query))
    key = urlparse(url).hostname + urlparse(url).path
    if len(value) < 2 or 'id' in value:
        return True

    # check the incoming url with the url hash table. If there are more than 5 urls having exactly the same queries with the incoming url,
    # the incoming url will be identified as a trap and therefore return False.
    if key in trapCheckTable and len(trapCheckTable[key]) >= 5:
        count = 0
        for item in trapCheckTable[key]:
            if value == item:
                count += 1
                if count >= 5:
                    return False
        trapCheckTable[key].append(value)
    elif key in trapCheckTable and len(trapCheckTable[key]) < 5:
        trapCheckTable[key].append(value)
    else:
        trapCheckTable[key] = [value]
    if trapCheckTable:
        print 'trapCheckTable inside', trapCheckTable
    return True


def save_data(fname, trapCheckTable, subDomainCount, invalid_links, max_out_link, trap_links, processed_urls, black_lists):
    with open(fname, 'w') as f:
        data = {}
        data['trapCheckTable'] = {}
        for k, v in trapCheckTable.items():
            data['trapCheckTable'][k] = []
            for v_set in v:
                data['trapCheckTable'][k].append(list(v_set))
        data['Sub Domain Count'] = subDomainCount
        data['Number of Invalid Links'] = len(invalid_links)
        data['URL with Max Out Links'] = max_out_link
        data['Invalid Links'] = invalid_links
        data['Trap Links'] = list(trap_links)
        data['Processed URLs'] = list(processed_urls)
        data['Black List'] = black_lists
        json.dump(data, f, indent=2, sort_keys=True, ensure_ascii=True)


def load_data(fname):
    trapCheckTable = {}  # for checking the trap in is_valid()
    subDomainCount = {}  # for counting the number of subdomain
    invalid_links = []
    trap_links = set()
    max_out_link = ['URL', 0]
    processed_urls = set()
    black_lists = []
    if os.path.exists(fname):
        copyfile(fname, fname + '.bk')
        with open(fname, 'r') as f:
            data = json.load(f)
            for k, v in data['trapCheckTable'].items():
                trapCheckTable[k] = []
                for v_list in v:
                    trapCheckTable[k].append(set(v_list))
            for k, v in data['Sub Domain Count'].items():
                subDomainCount[k] = int(v)
            invalid_links = data['Invalid Links']
            trap_links = set(data['Trap Links'])
            max_out_link = data['URL with Max Out Links']
            processed_urls = set(data['Processed URLs'])
            black_lists = data['Black List']
    return trapCheckTable, subDomainCount, invalid_links, trap_links, max_out_link, processed_urls, black_lists
