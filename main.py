#!/usr/bin/env python2
import argparse
import sys
import re
import requests
from HTMLParser import HTMLParser
import bs4 as bs


def phone_scrape(website):
    """Given possible ph# looks for ph#'s"""
    s = (r'1?\W*([2-9][0-8][0-9])\W*([2-9][0-9]'
         '{2})\W*([0-9]{4})(\se?x?t?(\d*))?')
    phone_numbers = re.findall(
        s, website)
    print
    print("Phone Numbers:")
    parsed_number = []
    for item in phone_numbers:
        area, mid, last, x, y = item
        corrected_number = area + '-' + mid + '-' + last
        if corrected_number not in parsed_number:
            print corrected_number
        parsed_number.append(corrected_number)


def url_scrape(website, soup_scrape):
    """Given possible url looks for url's"""
    # given options, looks for website
    # Divided regiex in half to meet the pep8 requirement
    first_half = 'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|'
    second_half = '(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    other_links = re.findall(
        first_half + second_half, website)
    print
    print("URL's")
    unique_handling = []
    for url in other_links:
        if url not in unique_handling:
            print(url)
            unique_handling.append(url)
    print
    print("Soup Data: Other URL's and Relative Url's based on domain or links")
    for url in soup_scrape:
        if url not in unique_handling:
            print(url)
            unique_handling.append(url)

    return other_links


def email_scrape(website):
    """ Given possible emails looks for emails """
    emails = re.findall(
        r'[\w\.-]+@[\w\.-]+', website)
    print
    print("Emails")
    already_printed = []
    for email in emails:
        if email not in already_printed:
            print(email)
            already_printed.append(email)
    print


def source_url(attrs):
    """ helpfer function for MyParser """
    for name, value in attrs:
        if 'src' or 'href' in name:
            return value
        else:
            return ''


class MyParser(HTMLParser):
    """ Limits the area's we look for emails,phone, and url
    by going through the page stepwise """

    def __init__(self):
        HTMLParser.__init__(self)
        self.in_script = False
        self.url_to_scrape = ''
        self.data_in_tags = ''

    def handle_starttag(self, tag, attrs):
        """Limits where website url's come from anddefines if in script """
        if tag == 'a' or tag == 'img':
            self.url_to_scrape += source_url(attrs) + ' '
        if tag == 'script':
            self.in_script = True

    def handle_endtag(self, tag):
        """ determines exit if in script"""
        if tag == 'script':
            self.in_script = False

    def handle_data(self, data):
        """Add data to search if not in script """
        if not self.in_script:
            if data:
                self.data_in_tags += data + ' '


def chunky_chicken_noodle(data):
    # print(data)
    soup_data = []
    soup = bs.BeautifulSoup(data, 'html.parser')
    for link in soup.find_all('a'):
        possible_url = link.get('href')
        if possible_url:
            soup_data.append(possible_url)
    for link in soup.find_all('img'):
        possible_url = link.get('src')
        if possible_url:
            soup_data.append(possible_url)
    return set(soup_data)


def web_request(website):
    """This is a handler """
    r = requests.get(website)
    soup_scrape = chunky_chicken_noodle(r.text)
    parser = MyParser()
    parser.feed(r.content)
    phone_scrape(parser.data_in_tags)
    email_scrape(parser.data_in_tags)
    url_scrape(parser.url_to_scrape, soup_scrape)


def create_parser():
    """ Arg parser """
    parser = argparse.ArgumentParser(description='Scrape a website')
    parser.add_argument(
        'url', help='Provide a website to scrape', nargs='+')
    return parser


def main():
    """ Main """
    parser = create_parser()
    args = parser.parse_args()

    if not args:
        parser.print_usage()
        sys.exit(1)

    if args.url:
        web_request(args.url[0])


if __name__ == "__main__":
    main()


# get urls only from a, href, and image tags -
# get phone numbers only from in between tags, not from attributes
# ignore all script sources because instructions unclear
#  usehtml parser ignore beautiful soup for now
# comments tell WHY and a lil of what
# helper and utility at top of page, big pic items at bottom
# - read from top to bottom in process order
