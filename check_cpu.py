#!/usr/bin/env python

"""
Icinga plugin to check CPU utilization on Linux systems. This is a pure Python
plugin, works with Python 2.6.x (requires argparse) and Python 2.7.x. Tested
on CentOS 7, CentOS 6 and Ubuntu 15.

It reads /proc/stat file two times in a configurable interval, then calculates
CPU usage in percentage, generates an alert if total cpu usage (user + sys +
nice + steal + softirq + iowait + irq) is greater than your thresholds.

Example:
    $ ./check_cpu.py
    CPU OK 0.85% in use | 'iowait'=0.25 'total'=100.00 'idle'=99.15 'user'=0.30 'softirq'=0.00 'steal'=0.00 'sys'=0.30 'irq'=0.00 'nice'=0.00 'inuse'=0.85

Project Page: http://www.ultrav.com.br/projetos/check-plugins/
Author: Vinicius Figueiredo <viniciusfs@gmail.com>
Version: 0.2.1

Change log:
  - 0.2.1 - Jan 31 2016 - Small fixes and cosmetic changes.
  - 0.2   - Jan 30 2016 - Added interval as command line argument.
  - 0.1   - Jan 28 2016 - First usable version.
"""


import re
import argparse

from collections import defaultdict
from copy import deepcopy
from sys import exit
from time import sleep


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def read_procfs():
    try:
        with open('/proc/stat', 'r') as stat_file:
            contents = stat_file.read()

            return contents

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)



def cpu_status():
    regex = re.compile(r'cpu  (?P<user>\d+)\s(?P<nice>\d+)\s(?P<sys>\d+)\s(?P<idle>\d+)\s(?P<iowait>\d+)\s(?P<irq>\d+)\s(?P<softirq>\d+)\s(?P<steal>\d+)')
    output = read_procfs()
    match = regex.search(output.split('\n')[0])

    if match:
        status = dict((k, float(v)) for k, v in match.groupdict().iteritems())
        status['perc_inuse'] = status['user'] \
            + status['nice'] + status['sys'] \
            + status['irq'] + status['softirq'] \
            + status['steal'] + status['iowait']
        status['total'] = status['idle'] + status['perc_inuse']

        return status
    else:
        return False


def diff_checks(first, second):
    diff = deepcopy(second)

    for k, v in first.iteritems():
        diff[k] -= v

    return diff


def calc_percentage(diff):
    usage = {}

    for k, v in diff.iteritems():
        usage[k] = (1000 * v / diff['total']) / 10

    return usage


def check_cpu(interval):
    first_check = cpu_status()
    sleep(interval)
    second_check = cpu_status()

    if first_check and second_check:
        diff = diff_checks(first_check, second_check)
        cpu_usage = calc_percentage(diff)

        return cpu_usage
    else:
        return False


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description="""Icinga plugin to check
    the amount of used CPU on Linux systems. It will generate an alert if
    CPU utilization (in percentage) is greater than your thresholds.
    """)

    parser.add_argument('-w', '--warning', action='store', dest='warning_threshold', type=int, default=80,
        help='Warning threshold. Returns warning if percentage of CPU usage is greater than this value. Default is 80.')
    parser.add_argument('-c', '--critical', action='store', dest='critical_threshold', type=int, default=90,
        help='Critical threshold. Returns critical if percentage of CPU usage is greater than this value. Default is 90.')
    parser.add_argument('-i', '--interval', action='store', dest='interval', type=int, default=5,
        help='Time delay in seconds between CPU info collects. Default is 5.')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
        help='No alert, only check CPU and print performance data.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.2.1')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold
    interval = arguments.interval
    noalert = arguments.noalert

    if warning > critical:
        print 'ERROR: warning threshold greater than critical threshold.'
        exit(UNKNOWN)

    if warning == critical:
        print 'ERROR: warning and critical threshold are equal.'
        exit(UNKNOWN)

    cpu_usage = check_cpu(interval)

    if cpu_usage:
        if cpu_usage['perc_inuse'] <= warning or noalert:
            print 'CPU %s %.2f%% in use | %s' % ('OK', cpu_usage['perc_inuse'], print_perfdata(cpu_usage))
            exit(OK)

        if cpu_usage['perc_inuse'] > warning and cpu_usage['perc_inuse'] < critical:
            print 'CPU %s %.2f%% in use | %s' % ('WARNING', cpu_usage['perc_inuse'], print_perfdata(cpu_usage))
            exit(WARNING)

        if cpu_usage['perc_inuse'] >= critical:
            print 'CPU %s %.2f%% in use | %s' % ('CRITICAL', cpu_usage['perc_inuse'], print_perfdata(cpu_usage))
            exit(CRITICAL)
    else:
        print 'ERROR: Fail while reading CPU information.'
        exit(UNKNOWN)



if __name__ == '__main__':
    main()

