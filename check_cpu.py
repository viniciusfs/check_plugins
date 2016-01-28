#!/usr/bin/env python

"""
Icinga plugin to check the amount of used CPU on Linux using /proc/stat file.

Some documentation about CPU usage calculation used while coding this script:
- http://stackoverflow.com/questions/23367857/accurate-calculation-of-cpu-usage-given-in-percentage-in-linux
- https://www.kernel.org/doc/Documentation/filesystems/proc.txt

Author: Vinicius Figueiredo <viniciusfs@gmail.com>
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

regex = re.compile(r'cpu  (?P<cpu_user>\d+)\s(?P<cpu_nice>\d+)\s(?P<cpu_sys>\d+)\s(?P<cpu_idle>\d+)\s(?P<cpu_iowait>\d+)\s(?P<cpu_irq>\d+)\s(?P<cpu_softirq>\d+)\s(?P<cpu_steal>\d+)')


def read_proc():
    try:
        with open('/proc/stat', 'r') as stat_file:
            usage_line = stat_file.readlines()[0]

        values = regex.search(usage_line)

        stats_dict = dict((k,float(v)) for k,v in values.groupdict().iteritems())

        stats_dict['cpu_inuse'] = stats_dict['cpu_user'] \
            + stats_dict['cpu_nice'] + stats_dict['cpu_sys'] \
            + stats_dict['cpu_irq'] + stats_dict['cpu_softirq'] \
            + stats_dict['cpu_steal'] + stats_dict['cpu_iowait']

        stats_dict['cpu_total'] = stats_dict['cpu_idle'] + stats_dict['cpu_inuse']

        return stats_dict

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)


def diff_checks(first, second):
    diff = deepcopy(second)

    for k,v in first.iteritems():
        diff[k] -= v

    return diff


def calc_percentage(diff):
    usage = {}

    for k, v in diff.iteritems():
        usage[k] = (1000 * v / diff['cpu_total']) / 10

    return usage


def check_cpu():
    first_check = read_proc()
    sleep(5)
    second_check = read_proc()

    diff = diff_checks(first_check, second_check)
    cpu_usage = calc_percentage(diff)

    return cpu_usage


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k.split('_')[1], v)

    return output


def main():
    parser = argparse.ArgumentParser(description='Icinga plugin to check the amount of used CPU on Linux using /proc/stat file.')

    parser.add_argument('-w', action='store', dest='warning_threshold', type=int, default=80,
        help='warning threshold. Returns warning if percentage of CPU usage is greater than this value. Default is 80.')
    parser.add_argument('-c', action='store', dest='critical_threshold', type=int, default=90,
        help='critical threshold. Returns critical if percentage of CPU usage is greater than this value. Default is 90.')
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

    cpu_usage = check_cpu()

    if cpu_usage['cpu_inuse'] <= warning:
        print 'CPU %s %.2f%% | %s' % ('OK', cpu_usage['cpu_inuse'], print_perfdata(cpu_usage))
        exit(OK)

    if cpu_usage['cpu_inuse'] > warning and cpu_usage['cpu_inuse'] < critical:
        print 'CPU %s %.2f%% | %s' % ('WARNING', cpu_usage['cpu_inuse'], print_perfdata(cpu_usage))
        exit(WARNING)

    if cpu_usage['cpu_inuse'] >= critical:
        print 'CPU %s %.2f%% | %s' % ('CRITICAL', cpu_usage['cpu_inuse'], print_perfdata(cpu_usage))
        exit(CRITICAL)



if __name__ == '__main__':
    main()

