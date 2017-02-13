#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest
from util import merge_path, remove_trailing_junk, is_repeated_path


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
        self.assertEqual(
            'http://www.ics.uci.edu/about/visit/../bren/bren_advance.php',
            remove_trailing_junk('http://www.ics.uci.edu/about/visit/../bren/bren_advance.php'))
        print remove_trailing_junk('http://www.ics.uci.edu/~pfbaldi?baldiPage=296')=='http://www.ics.uci.edu/~pfbaldi?baldiPage=296'

    def test_is_repeated_path(self):
        invalid_urls = [
            'http://www.ics.uci.edu/alumni/hall_of_fame/stayconnected/hall_of_fame/hall_of_fame/stayconnected/hall_of_fame/hall_of_fame/inductees.aspx.php',
            'http://www.ics.uci.edu/~mlearn/datasets/datasets/datasets/datasets/datasets/datasets/datasets/datasets/datasets/datasets/datasets/Abalone',
            'http://www.ics.uci.edu/alumni/hall_of_fame/stayconnected/stayconnected/stayconnected/hall_of_fame/stayconnected/stayconnected/hall_of_fame/index.php'
        ]
        for u in invalid_urls:
            self.assertTrue(is_repeated_path(u))
        valid_urls = [
            'http://www.ics.uci.edu/~pazzani/Publications/OldPublications.html',
            'http://www.ics.uci.edu/~theory/269/970103.html',
            'http://www.ics.uci.edu/~mlearn/datasets/datasets/CMU+Face+Images',
            'http://alderis.ics.uci.edu/files/AMBA_AHB_Functional_Verification_2Masters_Correct.out',
            'http://www.ics.uci.edu/~sharad',
            'http://www.ics.uci.edu/~sharad/students.html',
            'http://mhcid.ics.uci.edu',
            'http://www.ics.uci.edu/about/brenhall/index.php',
            'http://www.ics.uci.edu/~goodrich/pubs',
            'http://www.ics.uci.edu/alumni/stayconnected/hall_of_fame/inductees.aspx.php'
        ]
        for u in valid_urls:
            self.assertFalse(is_repeated_path(u))


if __name__ == '__main__':
    unittest.main()