__author__ = 'Praneetha'

import sqlite3
import re

# I will use this to convert all street abbreviations into their full name.
good_street_names = {'rd': 'Road',
                     'plz': 'Plaza',
                     'blvd': 'Boulevard',
                     'ave': 'Avenue',
                     'st': 'Street',
                     'hwy': 'Highway',
                     'ctr': 'Center',
                     'dr': 'Drive'}

# These are most of the common sources I saw in the top values
common_sources = ['bing', 'yahoo', 'google', 'survey', 'map', 'observation',
                  'knowledge', 'gps', 'yelp', 'website', 'gtfs', 'usgs']
common_webs = ['dot.ca.gov', 'yelp.com/biz']

def audit_phones(phone):
    """ Returns all phones that are able to be formatted in a similar way"""

    alphanumeric = re.compile('[a-zA-Z0-9]*')
    good_phone_format = re.compile('\+1\-[0-9A-Za-z]{3}\-[0-9A-Za-z]{3}\-[0-9A-Za-z]{4}')

    phone = re.findall(alphanumeric, phone)  # Gets alphanumeric characters in string
    phone = ''.join(phone)

    if phone[0] != '1':  # +1 is in U.S. numbers, add this number if it's not already present
        phone = '1'+phone

    if len(phone) == 11:  # Some phone numbers are missing digits, so check if there are 11
        phone = '+'+phone[0]+'-'+phone[1:4]+'-'+phone[4:7]+'-'+phone[7:]

    if not re.match(good_phone_format, phone):  # If the phone does not match the proper format, return None
        return None
    else:
        return phone


def audit_street(street):
    """Makes sure that the streets only contain the street name in its full, un-abbreviated form"""

    numbers_only = re.compile('^[0-9]*$')  # this will match to strings that only have numbers
    street = street.replace('.', '').replace('#', '').replace(',', '')  # remove common punctuation

    st_words = street.split(' ')
    first, last = st_words[0], st_words[-1]

    for j, word in enumerate(st_words):
        # Capitalize the first letter in each word
        st_words[j] = word.strip().title()

        # return a tuple of the street names if given two streets
        if word.lower() == 'and' or word.lower() == '&':
            double = street.split(word)
            return audit_street(double[0]), audit_street(double[1])

        # remove all numbers at the beginning and ending of string
        if word == first or word == last:
            if re.match(numbers_only, word):
                st_words[j] = ''

        # Remove suite from the street names.
        if word == 'Suite' or word == 'Ste':
            st_words[j] = ''

        # Replace street abbreviations with full name
        if word.lower().strip() in good_street_names.keys():
            st_words[j] = good_street_names[word.lower()]

    if '' in st_words:
        st_words.remove('')

    return ' '.join(st_words).strip()


def audit_sources(source):
    """This cleans the sources of information, by attempting to reduce variation"""

    if (';' in source) or (type(source) == tuple):
        # If there is more than one source, it's usually separated by a ';'. Return both
        try:
            double = source.split(';')
        except:
            double = source
        return audit_sources(double[0]), audit_sources(double[1])

    # If it's not a website, clean the string
    if 'http' not in source:
        source = source.replace('_', '')
        # If there is a common source in the string, replace it with the common source
        for cs in common_sources:
            if cs in source.lower():
                source = source.replace(source, cs)
    else:
        # If this a common website, make it less specific so you can group them together
        for cs in common_webs:
            if cs in source:
                source = source.rsplit('/', 1)[0]
    return source.lower().strip()