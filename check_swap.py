#!/usr/bin/env python

"""
Icinga plugin to check the amount of used swap on Linux using /proc/meminfo file.

Author: Vinicius Figueiredo <viniciusfs@gmail.com>
"""


import argparse

from sys import exit


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def read_proc():
    try:
        with open('/proc/meminfo', 'r') as meminfo_file:
            meminfo = {}
            for line in meminfo_file.readlines():
                try:
                    name, value = line.split(':')
                    meminfo[name.strip()] = float(value.split()[0])
                except:
                    pass
            swap_total = meminfo['SwapTotal']
            swap_free = meminfo['SwapFree']

        return swap_total, swap_free

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)


def check_swap():
    total, free = read_proc()
    perc_inuse = 100 - (free / total) * 100
    swap_usage = {
        'total': total,
        'free': free,
        'perc_inuse': perc_inuse
    }

    return swap_usage


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description='Icinga plugin to check the amount of used swap on Linux using /proc/meminfo.')

    parser.add_argument('-w', action='store', dest='warning_threshold', type=int, default=80,
        help='Warning threshold. Returns warning if percentage of swap usage is greater than this value. Default is 80.')
    parser.add_argument('-c', action='store', dest='critical_threshold', type=int, default=90,
        help='Critical threshold. Returns critical if percentage of swap usage is greater than this value. Default is 90.')
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

    swap_usage = check_swap()

    if swap_usage['perc_inuse'] <= warning:
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

