#!/usr/bin/env python

"""
Icinga plugin to check SWAP utilization on Linux systems. This is a pure Python
plugin, works with Python 2.6.x (requires argparse) and Python 2.7.x. Tested
on CentOS 7, CentOS 6 and Ubuntu 15.

It reads /proc/meminfo file to calculate swap utilization in percentage,
generates an alert if value is greater than your thresholds.

Example:
    $ check_swap.py
    Swap OK 0.00% in use | 'total'=8294396.00 'perc_inuse'=0.00 'free'=8294396.00

Project Page: http://www.ultrav.com.br/projetos/check-plugins/
Author: Vinicius Figueiredo <viniciusfs@gmail.com>
Version: 0.1.1

Change log:
  - 0.1.1 - Jan 31 2016 - Small fixes and cosmetic changes.
  - 0.1   - Jan 30 2016 - First usable version.
"""

import argparse
import re

from sys import exit


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def read_procfs():
    try:
        with open('/proc/meminfo', 'r') as data_file:
            contents = data_file.read()

            return contents

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)


def swap_status():
    regex = re.compile(r'SwapTotal:\s+(?P<swap_total>\d+)\skB\nSwapFree:\s+(?P<swap_free>\d+)\skB\n')
    output = read_procfs()
    match = regex.search(output)

    if match:
        status = dict((k, float(v)) for k, v in match.groupdict().iteritems())
        return status
    else:
        return False


def check_swap():
    swap_usage = swap_status()

    if swap_usage:
        swap_usage['perc_inuse'] = 100 - (swap_usage['swap_free'] / swap_usage['swap_total']) * 100

        return swap_usage
    else:
        return False


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description="""Icinga plugin to check the
    amount of used swap on Linux systems. It calculates swap utilization in
    percentage and generates an alert if value is greater than your thresholds.
    Performance data output in kB.
    """)

    parser.add_argument('-w', '--warning', action='store', dest='warning_threshold', type=int, default=80,
        help='Warning threshold. Returns warning if percentage of swap usage is greater than this value. Default is 80.')
    parser.add_argument('-c', '--critical', action='store', dest='critical_threshold', type=int, default=90,
        help='Critical threshold. Returns critical if percentage of swap usage is greater than this value. Default is 90.')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
        help='No alert, only check swap and print performance data.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.1')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold
    noalert = arguments.noalert

    if warning > critical:
        print 'ERROR: warning threshold greater than critical threshold.'
        exit(UNKNOWN)

    if warning == critical:
        print 'ERROR: warning and critical threshold are equal.'
        exit(UNKNOWN)

    swap_usage = check_swap()

    if swap_usage:
        if swap_usage['perc_inuse'] <= warning or noalert:
            print 'Swap %s %.2f%% in use | %s' % ('OK', swap_usage['perc_inuse'], print_perfdata(swap_usage))
            exit(OK)

        if swap_usage['perc_inuse'] > warning and swap_usage['perc_inuse'] < critical:
            print 'Swap %s %.2f%% in use | %s' % ('WARNING', swap_usage['perc_inuse'], print_perfdata(swap_usage))
            exit(WARNING)

        if swap_usage['perc_inuse'] >= critical:
            print 'Swap %s %.2f%% in use | %s' % ('CRITICAL', swap_usage['perc_inuse'], print_perfdata(swap_usage))
            exit(CRITICAL)



if __name__ == '__main__':
    main()
