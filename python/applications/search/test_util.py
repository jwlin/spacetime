#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from util import merge_path, remove_trailing_junk


class TestCrawlerFrame(unittest.TestCase):
    def test_merge_path(self):
        self.assertEqual('/about/annualreport/index.php', merge_path('/a/b/', '../../../about/annualreport/index.php'))
        self.assertEqual('/about/annualreport/index.php', merge_path('/', '../../../about/annualreport/index.php'))
        self.assertEqual('/about/annualreport/index.php', merge_path('/a/', '../about/annualreport/index.php'))
        self.assertEqual('/annualreport/index.php', merge_path('/', '../about/../../annualreport/index.php'))
        self.assertEqual('/annualreport/index.php', merge_path('/', 'about/../annualreport/index.php'))
        self.assertEqual('/a/about/annualreport/index.php', merge_path('/a/b/', '../about/annualreport/index.php'))

    def test_remove_trailing_junk(self):
        self.assertEqual(
            'http://www.ics.uci.edu?p=2&c=igb-misc',
            remove_trailing_junk('http://www.ics.uci.edu?p=2&c=igb-misc/degrees/index/'))
        self.assertEqual(
            'http://www.ics.uci.edu/computing/linux/shell.php',
            remove_trailing_junk('http://www.ics.uci.edu/computing/linux/shell.php/computing/account/'))
        self.assertEqual(
            'http://www.ics.uci.edu/about/search/index.php',
            remove_trailing_junk('http://www.ics.uci.edu/about/search/index.php/about_safety.php/grad/index.php/search_payroll.php/search_graduate.php/search_sao.php/search_dean.php/search_dept_in4matx.php/search_business.php/search_dept_stats.php/search_support.php/search_facilities.php/search_payroll.php/ugrad/index.php/search_graduate.php/about_deanmsg.php/search_dean.php/ICS/ics/about/bren/index.php/about_contact.php/search_dept_stats.php/index.php/bren/index.php/ICS/ICS/search_dept_stats.php/search_business.php/search_external.php/ugrad/search_dept_cs.php/search_sao.php/search_dean.php/../about_safety.php/../about_meet_the_dean.php/../../grad/index.php'))

if __name__ == '__main__':
    unittest.main()