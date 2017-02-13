import logging
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
from bs4 import BeautifulSoup
#from lxml import html,etree
import re, os
from time import time
import requests
from shutil import copyfile
from util import merge_path, remove_trailing_junk, is_not_trap, save_data, load_data

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
MAX_LINKS_TO_DOWNLOAD = 1600

data_fname = 'data.json'
trapCheckTable, subDomainCount, invalid_links, trap_links, max_out_link, processed_urls, black_lists = load_data(data_fname)
copyfile('successful_urls.txt', 'successful_urls.txt.bk')

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
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
        save_data(data_fname, trapCheckTable, subDomainCount, invalid_links, max_out_link, trap_links, processed_urls, black_lists)
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
    global invalid_links
    global max_out_link
    print 'len of rawDatas', len(rawDatas)
    for element in rawDatas:
        #print 'error_message', element.error_message
        #print 'http_code', element.http_code
        #print 'headers', element.headers
        print 'is_redirected', element.is_redirected
        print 'final_url', element.final_url
        print 'bad_url', element.bad_url
        #print 'out_links', element.out_links
        print '---'
        #raw_input()

        countSubDomain(element.url)

        if str(element.http_code) != '200':
            invalid_links.append(element.url)
            element.bad_url = True
            print 'wrong http_code'
            continue

        src_url = element.url
        if element.is_redirected:
            src_url = element.final_url
            print 'redirected', src_url

        if not is_valid(src_url):
            element.bad_url = True
            invalid_links.append(element.url)
            print 'not valid'
            continue

        src_url = remove_trailing_junk(src_url)  # remove trailing string after parameters
        print 'src_url:', src_url
        parsed = urlparse(src_url)
        print 'parsed', parsed
        print '---'
        # check if there is username:password@hostname
        credential = ''
        if parsed.username:
            credential = parsed.username
            credential += ':' + parsed.password + '@' if parsed.password else '@'

        #path = parsed.path[:-1] if parsed.path and parsed.path[-1] == '/' else parsed.path
        path = parsed.path
        # path: '/a/b/c.html' -> '/a/b/'
        path = '/'.join(path.split('/')[:-1]) + '/'
        url_prefix = parsed.scheme + '://' + credential + parsed.hostname

        soup = BeautifulSoup(element.content, 'html.parser')
        links = soup.find_all('a')
        num_o_link = 0
        for link in links:
            print link
            o_link = ''
            if 'href' in link.attrs.keys():
                href = link['href']
                href = remove_trailing_junk(href)
                if '#' in href:
                    href = re.sub(r'#.*', '', href)
                if href.startswith('./'):
                    href = href[2:]
                if href.startswith('mailto') or not href:
                    pass
                    #print 'Not an URL'
                elif href.startswith('/'):
                    o_link = url_prefix + href
                elif href.startswith('http'):
                    o_link = href
                elif '../' in href:
                    o_link = url_prefix + merge_path(path, href)
                else:
                    o_link = url_prefix + path + href
                if o_link:
                    print o_link
                    num_o_link += 1
                    outputLinks.append(o_link)
                #raw_input()
        if num_o_link > max_out_link[1]:
            max_out_link = [element.url, num_o_link]
    #print 'invalid_links', len(invalid_links)
    #print 'max_out_link', max_out_link
    #print 'subDomainCount', subDomainCount
    #print 'trap_links', trap_links
    save_data(data_fname, trapCheckTable, subDomainCount, invalid_links, max_out_link, trap_links, processed_urls, black_lists)
    return outputLinks


def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be downloaded or not.
    Robot rules and duplication rules are checked separately.

    This is a great place to filter out crawler traps.
    '''
    #global invalidLinkCount
    global trapCheckTable
    global trap_links

    #the url must be start with http and https, and only website from ics.uci.edu, not ending with the following file format
    parsed = urlparse(url)
    if parsed.scheme not in set(["http", "https"]):
        #invalidLinkCount += 1
        return False
    try:
        if ".ics.uci.edu" not in parsed.hostname \
               or re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf|ppsx" \
                                + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                + "|thmx|mso|arff|rtf|jar|csv|txt|py|lif|h5" \
                                + "|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            # http://mlphysics.ics.uci.edu/data/hepjets/images/test_no_pile_5000000.h5
            # #invalidLinkCount += 1
            return False
    except TypeError:
        print ("TypeError for ", parsed)

    for bl in black_lists:
        if bl in url:
            return False

    #checking is the website connectable
    try:
        check = requests.get(url)
        if check.status_code != 200:
            #invalidLinkCount += 1
            return False
    except requests.RequestException:
        #invalidLinkCount += 1
        return False

    if url != remove_trailing_junk(url):
        return False

    if is_not_trap(url, trapCheckTable):
        return True
    else:
        trap_links.add(url)
        return False


# counting the numbers of subdomain, please execute is_valid to determine using this function
def countSubDomain(url):
    global subDomainCount
    global processed_urls
    if url.strip() not in processed_urls:
        processed_urls.add(url)
        parsed = urlparse(url)
        subDomain = re.sub('\.ics\.uci\.edu', '', parsed.hostname)
        if subDomain in subDomainCount:
            subDomainCount[subDomain] += 1
        else:
            subDomainCount[subDomain] = 1
