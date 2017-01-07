#!/usr/bin/env python

"""
This file is part of ultrav check_plugins project
http://github.com/viniciusfs/check_plugins
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


def memory_status():
    regex1 = re.compile(r'MemTotal:\s+(?P<total>\d+)\skB\nMemFree:\s+(?P<free>\d+)\skB\n')
    regex2 = re.compile(r'Buffers:\s+(?P<buffers>\d+)\skB\nCached:\s+(?P<cached>\d+)\skB\n')

    output = read_procfs()

    match1 = regex1.search(output)
    match2 = regex2.search(output)

    if match1 and match2:
        status = dict((k, float(v)) for k, v in match1.groupdict().iteritems())

        for k, v in match2.groupdict().iteritems():
            status.update({ k: float(v) })
        return status
    else:
        return False


def check_mem():
    mem_usage = memory_status()

    if mem_usage:
        mem_usage['used'] = mem_usage['total'] - (mem_usage['free'] + mem_usage['buffers'] + mem_usage['cached'])
        mem_usage['perc_inuse'] = 100 - ((mem_usage['free'] + mem_usage['buffers'] + mem_usage['cached']) / mem_usage['total']) * 100

        return mem_usage
    else:
        return False


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description='Icinga plugin to check the amount of used memory on Linux using /proc/meminfo.')

    parser.add_argument('-w', '--warning',  action='store', dest='warning_threshold', type=int, default=80,
        help='Warning threshold. Returns warning if percentage of memory usage is greater than this value. Default is 80.')
    parser.add_argument('-c', '--critical', action='store', dest='critical_threshold', type=int, default=90,
        help='Critical threshold. Returns critical if percentage of memory usage is greater than this value. Default is 90.')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
            help='No alert, only check memory and print performance data.')
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

    memory_usage = check_mem()

    if memory_usage:
        if memory_usage['perc_inuse'] <= warning or noalert:
            print 'Memory %s %.2f%% in use | %s' % ('OK', memory_usage['perc_inuse'], print_perfdata(memory_usage))
            exit(OK)

        if memory_usage['perc_inuse'] > warning and memory_usage['perc_inuse'] < critical:
            print 'Memory %s %.2f%% in use | %s' % ('WARNING', memory_usage['perc_inuse'], print_perfdata(memory_usage))
            exit(WARNING)

        if memory_usage['perc_inuse'] >= critical:
            print 'Memory %s %.2f%% in use | %s' % ('CRITICAL', memory_usage['perc_inuse'], print_perfdata(memory_usage))
            exit(CRITICAL)



if __name__ == '__main__':
    main()

