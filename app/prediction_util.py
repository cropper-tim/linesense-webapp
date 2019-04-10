import numpy as np
import statistics as stat
from scipy import stats
import datetime


# calculate the start time for the user input (for fetching line length)
def calc_in_line_time(timestamp, duration):
    return timestamp - datetime.timedelta(seconds=duration)


# return the mean and stddev from a set of service rates
def line_stats(service_rates):
    if not service_rates:
        return [0, 0]

    trimmed_rates = stats.trimboth(service_rates, 0.1)
    mean = stat.mean(trimmed_rates)
    stddev = stat.stdev(trimmed_rates, mean)

    return [mean, stddev]
