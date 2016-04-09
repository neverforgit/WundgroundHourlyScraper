import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from statsmodels.distributions.empirical_distribution import ECDF

__author__ = "Andrew Campbell"

######################################################################################################################
# Worker functions
######################################################################################################################
# These are the functions that do all the heavy lifting

def data_files_to_df(data_dir, concat_intv=10, cols=None, datfrmt='.csv'):
    """
    Reads all the csv data files into one big Pandas DataFrame.
    :param data_dir: (str) Path to the directory with the data files.
    :param concat_intv: (int) The number of files to open and convert to data frame before
    aggregating. It would be fastest to open everything and concat only once. But this could cause memory problems.
    :param cols: ([str]) Names of columns from data files to be kept. If None, keeps everything.
    :param datfrmt: (str) Format of data files.
    :return: (pd.DataFrame) DataFrame from all the rows from the data files.
    """
    odir = os.getcwd()
    os.chdir(data_dir)  # Move to the data directory for working
    # Get a list of all data file names. Grabs all files of type datfrmt
    fnames = [n for n in os.listdir(data_dir) if n[-len(datfrmt):] == datfrmt]

    # Set the columns
    if not cols:
        temp = pd.read_csv(fnames[0])
        cols = temp.columns.tolist()

    # Concat all the data files
    df = pd.DataFrame(columns=cols)
    temp_list = [df]
    for name in fnames:
        print 'Adding file: %s' % name
        try:
            temp = pd.read_csv(name, usecols=cols, index_col=False)
        except TypeError:  # Thrown when no data available for that date. Only the header is served
            continue
        temp_list.append(temp)
        if len(temp_list) == concat_intv:
            temp_list = [pd.concat(temp_list)]
    os.chdir(odir)  # Move back to the calling directory
    return pd.concat(temp_list)

def hourly_averages(data_df):
    """
    Takes the output from data_files_to_df and calculates hourly averages for each date. In other words, each day
    should be reduced to 24 average hourly observations.
    :param data_df: (pd.DataFrame) Output from data_files_to_df.
    :return: (pd.DataFrame) Hourly averages for each day. Uses a MultiIndex of day-hour. If you are only averaging one
    variable, then it might be cleaner to unstack it. But if you are averaging multiple variables it is much nicer
    to use the MultiIndex. Pandas writes one unique row for each unique MultiIndex tuple.
    """
    # Add day and hour columns
    data_df['day'] = data_df.apply(lambda row: row['Time'][0:10], axis=1)
    data_df['hour'] = data_df.apply(lambda row: row['Time'][-8:-6], axis=1)
    # Groupby day and hour
    g = data_df.groupby(['day', 'hour'])
    return g.mean()

def plot_hoursbelow_dist(mean_df, fig_path, metric='TemperatureF', total_hours=False):
    """
    Takes the output of hourly_averages and plots the distribution of hours below certain metric (i.e. the cdf cast
    to hours instead of percentiles). This is useful for calculating the annual chilling hours.
    :param mean_df: (pd.DataFrame) Output of hourly_averages. Each row is a unique hour from a unique day.
    :param fig_path: (str) Path to save figure out.
    :param metric: (str) Metric to be analysed.
    :param total_hours: (bool) If True, calculates the distribution over all hours in the mean_df. If False, reports
    expected hours for one 365-day year.
    :return: (pd.DataFrame)
    """

    # Caclulate the empirical CDF
    ecdf = ECDF(mean_df[metric])
    m = mean_df[metric].tolist()
    m.sort()
    if total_hours:
        hours = mean_df.shape[0]
    else:
        hours = 24*365
    dist = ecdf(mean_df[metric])
    dist.sort()
    # Cast to hours and create df
    df_dist = pd.DataFrame(data={metric: m, 'hours': dist*hours})
    # Plot
    #fig = plt.figure(figsize=(12, 8))
    #plt.plot(df_dist['hours'], df_dist[metric], linewidth=2.0)
    fig, ax = plt.subplots()
    fig.set_size_inches(10, 8)
    ax.plot(df_dist['hours'], df_dist[metric], linewidth=2.0)
    ax.grid(b=True, which='major', linestyle='-')
    ax.grid(b=True, which='minor', linestyle=':')
    ax.fill_between(df_dist['hours'], df_dist[metric], 0, facecolor='green', alpha=0.5)
    plt.xlabel('hours', fontsize=18)
    plt.ylabel(metric, fontsize=18)
    plt.minorticks_on()
    plt.savefig(fig_path)
    return df_dist




