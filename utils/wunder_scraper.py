import logging
import os.path
import time
import urllib
import urlparse

from datetime import date, timedelta

import numpy.random
import requests

__author__ = "Andrew Campbell"

"""
This script is used to automate the downloading of files from the Weather Underground history.
"""

##
# Functions
##

def daterange(start_date, end_date):
    """
    Returns an iterator for cycling through dates. Only yields true dates (i.e. no February 30).
    :param start_date (datetime.date) Start date.
    :param end_date (datetime.date) End date.
    :return (iterator)
    """
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def build_url(dt, base_url, url_params):
    """
    Builds the complete url for querying wunderground history.
    :param dt: (datetime.date) Date of query
    :param base_url: (str) url prefix used in each query
    :param url_params: (dict) Elements necessary to build the url
        id = unique identifier of the wunderground station
        graphspan =  dictates aggregation and resolution. Use 'day' for the finest resolution
        format = not clear what this does. I use the default value of 1
    :return: (str) url string
    """
    url_params['year'] = dt.year
    url_params['month'] = dt.month
    url_params['day'] = dt.day
    parse = urlparse.urlparse(base_url)
    q = urllib.urlencode(url_params)
    parse = parse._replace(query=q)
    return urlparse.urlunparse(parse)

def scrape_history(start_date, end_date, base_url, url_params, sleep_time, out_dir, log_path):

    """
    Requests the history page for each day in between, and including, start_date and end_date. The pages
    are saved to csv files.
    :param start_date: (datetime.date) Starting date of history to be scraped.
    :param end_date: (datetime.date) Ending date of history to be scraped.
    :param base_url: (str) url prefix used in each query
    :param url_params: (dict) The invarianet elements necessary to construct the url query string. Includes:
        id = unique identifier of the wunderground station
        graphspan =  dictates aggregation and resolution. Use 'day' for the finest resolution
        format = not clear what this does. I use the default value of 1
    :param sleep_time: (int | double) Number of seconds to sleep between querries.
    :param out_dir: (str) Directory of output files.
    :param log_path: (str) Path of logging file.
    :return: (int) Number of files downloaded.
    """
    # Start logger
    logging.basicConfig(filename=log_path, level=logging.DEBUG)
    logging.info("Start Scraping")

    # Start scraping
    dr = daterange(start_date, end_date)
    for i, dt in enumerate(dr):
        ts = sleep_time
        # Following block will try to request the url at ever increasing sleep times.
        while True:
            try:  # try to request url w/ default sleep time
                print 'Downloading file number %d' % i
                logging.info('attempt download file no. %d' % i)
                logging.info('time to sleep ' + str(ts))
                url = build_url(dt, base_url, url_params)
                r = requests.get(url)
                #TODO check if any data is in the returned page. Wunderground will serve up just the column names
                #TODO with no rows when no data exists.
                # Request has been served succesfully, so write it to a csv
                out_path = os.path.join(out_dir, dt.strftime('%Y_%m_%d.csv'))
                #TODO write a helper function to cleanup the output csv files. The current version includes a bunch of
                #TODO stupid blank lines. However, Pandas is perfectly capable of parsing these csvs into dataframes.
                with open(out_path, 'wb') as fo:
                    fo.write(r.text.replace('<br>', ''))  # remove the annoying <br> tags at the end of each line
                # Sleep for a random time centered on sleep_time
                time.sleep(numpy.random.random_integers(0.8*sleep_time, 1.2*sleep_time))
            except requests.ConnectionError:
                logging.warning('ConnectionError')
                ts = ts*2
                time.sleep(ts)
                continue
            break




