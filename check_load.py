#!/usr/bin/env python

"""
Icinga plugin to check load average on Linux.

Author: Vinicius Figueiredo <viniciusfs@gmail.com>
"""


import argparse

from sys import exit


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def check_load():
    try:
        with open('/proc/loadavg', 'r') as load_file:
            line = load_file.readlines()[0]
            load1, load5, load15 = float(line.split()[0]), float(line.split()[1]), float(line.split()[2])

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)

    load_average = {
        'load1': load1,
        'load5': load5,
        'load15': load15,
    }

    return load_average


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description='Icinga plugin to check load average on Linux.')

    parser.add_argument('-w', action='store', dest='warning_threshold', type=float, default=1,
        help='Warning threshold. Returns warning if percentage of swap usage is greater than this value. Default is 1.')
    parser.add_argument('-c', action='store', dest='critical_threshold', type=float, default=2,
        help='Critical threshold. Returns critical if percentage of swap usage is greater than this value. Default is 2.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold

    if warning > critical:
        print 'ERROR: warning threshold greater than critical threshold.'
        exit(UNKNOWN)

    if warning == critical:
        print 'ERROR: warning and critical threshold are equal.'
        exit(UNKNOWN)

    load_average = check_load()

    if load_average['load1'] <= warning:
        print 'Load average %s %.2f%% | %s' % ('OK', load_average['load1'], print_perfdata(load_average))
        exit(OK)

    if load_average['load1'] > warning and load_average['load1'] < critical:
        print 'Load average %s %.2f%% | %s' % ('WARNING', load_average['load1'], print_perfdata(load_average))
        exit(WARNING)

    if load_average['load1'] >= critical:
        print 'Load average %s %.2f%% | %s' % ('CRITICAL', load_average['load1'], print_perfdata(load_average))
        exit(CRITICAL)



if __name__ == '__main__':
    main()

