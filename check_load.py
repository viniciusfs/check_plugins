#!/usr/bin/env python

"""
Icinga plugin to check load average on Linux systems. This is a pure Python
plugin, works with Python 2.6.x (requires argparse) and Python 2.7.x. Tested
on CentOS 7, CentOS 6 and Ubuntu 15.

It reads /proc/loadavg file and generate an alert if load1 value is greater
than your thresholds.

Example:
    $ check_load.py
    Load average OK 0.25 | 'load1'=0.25 'load15'=0.13 'load5'=0.10

Project Page: http://www.ultrav.com.br/projetos/check-plugins/
Author: Vinicius Figueiredo <viniciusfs@gmail.com>
Version: 0.1.2

Change log:
  - 0.1.2 - Mar 23 2016 - Added CPU count option.
  - 0.1.1 - Jan 31 2016 - Small fixes and cosmetic changes.
  - 0.1   - Jan 30 2016 - First usable version.
"""

import argparse
import multiprocessing

from sys import exit


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def read_procfs():
    try:
        with open('/proc/loadavg', 'r') as data_file:
            contents = data_file.read()

            return contents

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)


def load_status():
    output = read_procfs()
    load1, load5, load15, nprocs, last_pid = output.split()

    status = {
        'load1': float(load1),
        'load5': float(load5),
        'load15': float(load15),
    }

    return status


def check_load():
    load_usage = load_status()

    return load_usage


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description="""Icinga plugin to check
    current load average on Linux systems. It will generate an alert if load1
    value is greater than your thresholds.
    """)

    parser.add_argument('-w', '--warning', action='store', dest='warning_threshold', type=float, default=1,
        help='Warning threshold. Returns warning if load1 is greater than this value. Default is 1.')
    parser.add_argument('-c', '--critical', action='store', dest='critical_threshold', type=float, default=2,
        help='Critical threshold. Returns critical if load1 is greater than this value. Default is 2.')
    parser.add_argument('--cpu-count', action='store_true', dest='cpucount',
        help='Divides load per CPU count before test against thresholds.')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
        help='No alert, only check and print performance data.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.2')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold
    noalert = arguments.noalert
    cpucount = arguments.cpucount

    if warning > critical:
        print 'ERROR: warning threshold greater than critical threshold.'
        exit(UNKNOWN)

    if warning == critical:
        print 'ERROR: warning and critical threshold are equal.'
        exit(UNKNOWN)

    load_average = check_load()

    if cpucount:
        load = load_average['load1'] / multiprocessing.cpu_count()
    else:
        load = load_average['load1']

    if load <= warning or noalert:
        print 'Load average %s %.2f, %.2f, %.2f | %s' % ('OK', load_average['load1'], load_average['load5'], load_average['load15'], print_perfdata(load_average))
        exit(OK)

    if load > warning and load < critical:
        print 'Load average %s %.2f, %.2f, %.2f | %s' % ('WARNING', load_average['load1'], load_average['load5'], load_average['load15'], print_perfdata(load_average))
        exit(WARNING)

    if load >= critical:
        print 'Load average %s %.2f, %.2f, %.2f | %s' % ('CRITICAL', load_average['load1'], load_average['load5'], load_average['load15'], print_perfdata(load_average))
        exit(CRITICAL)



if __name__ == '__main__':
    main()
