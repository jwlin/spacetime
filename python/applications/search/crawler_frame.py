import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
from bs4 import BeautifulSoup
#from lxml import html,etree
import re, os
from time import time
import requests

try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set() 
    if not os.path.exists("successful_urls.txt") else 
    set([line.strip() for line in open("successful_urls.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 3000
trapCheckTable = {}    #for checking the trap in is_valid()
invalidLinkCount = 0   #for counting the invalid link

@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):
    def __init__(self, frame):
        self.starttime = time()
        # Set app_id <student_id1>_<student_id2>...
        self.app_id = "44457392_13802479_32887430"
        # Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
        # If Graduate studetn, change the UnderGrad part to Grad.
        self.UserAgentString = "IR W17 Grad 44457392,13802479,32887430"

        self.frame = frame
        assert(self.UserAgentString != None)
        assert(self.app_id != "")
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        for g in self.frame.get(OneUnProcessedGroup):
            print "Got a Group"
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
                if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
                    urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            for l in outputLinks:
                print l, is_valid(l)
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
        pass


def save_count(urls):
    global url_count
    urls = set(urls).difference(url_count)
    url_count.update(urls)
    if len(urls):
        with open("successful_urls.txt", "a") as surls:
            surls.write(("\n".join(urls) + "\n").encode("utf-8"))


def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas
    
#######################################################################################
'''
STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.
'''


def extract_next_links(rawDatas):
    outputLinks = list()
    '''
    rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
    Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
    the return of this function should be a list of urls in their absolute form
    Validation of link via is_valid function is done later (see line 42).
    It is not required to remove duplicates that have already been downloaded.
    The frontier takes care of that.

    Suggested library: lxml
    '''
    global invalidLinkCount
    print 'len of rawDatas', len(rawDatas)
    for element in rawDatas:
        print element.error_message
        print element.http_code
        print element.headers
        print element.is_redirected
        print element.final_url
        print element.bad_url
        print element.out_links
        raw_input()

        if element.http_code != '200':
            invalidLinkCount += 1
            element.bad_url = True
            continue

        if element.is_redirected:
            src_url = element.final_url
        print 'src_url:', src_url

        if not is_valid(src_url):
            element.bad_url = True
            continue

        # remove trailing string after parameters
        # e.g. http://www.ics.uci.edu?p=2&c=igb-misc/degrees/index/grad/... ->  http://www.ics.uci.edu?p=2&c=igb-misc
        if '?' in src_url and '/' in src_url[src_url.index('?'):]:
            src_url = src_url[
                src_url.index('?') +
                src_url[src_url.index('?'):].index('/')
            ]

        parsed = urlparse(src_url)
        # check if there is username:password@hostname
        credential = ''
        if parsed.username:
            credential = parsed.username
            credential += ':' + parsed.password + '@' if parsed.password else '@'
        # remove trailing '/'
        print parsed
        path = parsed.path[:-1] if parsed.path and parsed.path[-1] == '/' else parsed.path
        # path: '/a/b/c.html' -> '/a/b/'
        path = '/'.join(path.split('/')[:-1]) + '/'
        url_prefix = parsed.scheme + '://' + credential + parsed.hostname

        soup = BeautifulSoup(element.content, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            print link
            o_link = ''
            if 'href' in link.attrs.keys():
                href = link['href']
                if '#' in href:
                    href = re.sub(r'#.*', '', href)
                if href.startswith('mailto') or not href:
                    print 'Not an URL'
                elif href.startswith('/'):
                    o_link = url_prefix + href
                elif href.startswith('http'):
                    o_link = href
                else:
                    o_link = url_prefix + path + href
                    # todo:
                    # ../../../about/annualreport/index.php
                    # <a href="../Author/David-J-Pearce.html">David J. Pearce</a>
                    # http://fano.ics.uci.edu/cites/Document/../Author/David-J-Pearce.html
                    # http://fano.ics.uci.edu/cites/Author/David-J-Pearce.html
                    # <a href="?s=people">People</a>
                if o_link:
                    print o_link
                    outputLinks.append(o_link)
                raw_input()
    return outputLinks


def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be downloaded or not.
    Robot rules and duplication rules are checked separately.

    This is a great place to filter out crawler traps.
    '''
    global invalidLinkCount
    global trapCheckTable
    #checking is the website connectable
    try:
        check = requests.get(url)
        if check.status_code != 200:
            invalidLinkCount += 1
            return False
    except requests.RequestException:
        invalidLinkCount += 1
        return False

    #the url must be start with http and https, and only website from ics.uci.edu, not ending with the following file format
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        invalidLinkCount += 1
        return False
    try:
        if ".ics.uci.edu" not in parsed.hostname \
               or re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                + "|thmx|mso|arff|rtf|jar|csv" \
                                + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            invalidLinkCount += 1
            return False
    except TypeError:
        print ("TypeError for ", parsed)

    #detecting the trap

    value = parse_qs(urlparse(url).query)
    key = urlparse(url).netloc + urlparse(url).path

    if len(set(value)) < 2 or 'id' in set(value):
        return True


    # check the incoming url with the url hash table. If there are more than 5 urls having exactly the same queries with the incoming url, 
    # the incoming url will be identified as a trap and therefore return False.
    if key in trapCheckTable and len(trapCheckTable[key]) >= 5:
        count = 0
        for item in trapCheckTable[key]:
            if set(value) == set(item):
                count += 1
                if count >= 5:
                    return False
        trapCheckTable[key].append(value)
        return True
    elif key in trapCheckTable and len(trapCheckTable[key]) < 5:
        trapCheckTable[key].append(value)
        return True
    else:
        trapCheckTable[key] = [value]
        return True

