import ConfigParser
import datetime
import sys

import utils.wunder_scraper

__author__ = 'Andrew A Campbell'

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'ERROR: need to supply the path to the conifg file'
    # Load the config paths and parameters.
    config_path = sys.argv[1]
    conf = ConfigParser.ConfigParser()
    conf.read(config_path)
    #Paths
    log_path = conf.get('Paths', 'log_path')
    out_dir = conf.get('Paths', 'out_dir')
    #Params
    base_url = conf.get('Params', 'base_url')
    start_date = [int(x) for x in [y.strip() for y in conf.get('Params', 'start_date').split(',')]]
    start_date = datetime.date(start_date[0], start_date[1], start_date[2])
    end_date = [int(x) for x in [y.strip() for y in conf.get('Params', 'end_date').split(',')]]
    end_date = datetime.date(end_date[0], end_date[1], end_date[2])
    station_id = conf.get('Params', 'station_id')
    graphspan = conf.get('Params', 'graphspan')
    frmt = int(conf.get('Params', 'format'))
    sleep_time = int(conf.get('Params', 'sleep_time'))

    # Build the url query parameters dict
    url_params = {'ID': station_id, 'graphspan': graphspan, 'format': frmt}

    # Download the datas!
    utils.wunder_scraper.scrape_history(start_date, end_date, base_url, url_params, sleep_time, out_dir, log_path)
