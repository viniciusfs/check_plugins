#!/usr/bin/env python 

"""
Icinga plugin to check network utilization on Linux systems. This is a pure
Python plugin, works with Python 2.6.x (requires argparse) and Python 2.7.x.
Tested on CentOS 7, CentOS 6 and Ubuntu 15.

It reads /proc/net/dev file two times in a configurable interval, then
calculates network utilization in kB/s and packets per second. Generates an
alert if values are greater than your thresholds.

Example:
    $ ./check_network.py

Project Page: http://www.ultrav.com.br/projetos/check-plugins/
Author: Vinicius Figueiredo <viniciusfs@gmail.com>
Version: 0.1

Change log:
  - 0.1   - Jan 31 2016 - First usable version.
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
        with open('/proc/net/dev', 'r') as data_file:
            contents = data_file.read()

            return contents

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)


def iface_status(iface):
    regex = re.compile(r'%s:\s+(?P<rx_bytes>\d+)\s+(?P<rx_packets>\d+)\s+(?P<rx_errs>\d+)\s+(?P<rx_drop>\d+)\s+(?P<rx_fifo>\d+)\s+(?P<rx_frame>\d+)\s+(?P<rx_compressed>\d+)\s+(?P<rx_multicast>\d+)\s+(?P<tx_bytes>\d+)\s+(?P<tx_packets>\d+)\s+(?P<tx_errs>\d+)\s+(?P<tx_drop>\d+)\s+(?P<tx_fifo>\d+)\s+(?P<tx_colls>\d+)\s+(?P<tx_compressed>\d+)' % iface)
    output = read_procfs()
    match = regex.search(output)

    if match:
        status = dict((k, float(v)) for k, v in match.groupdict().iteritems())
        return status
    else:
        return False


def valid_iface(device):
    regex = re.compile(r'(?P<iface>\w+\d):\s')
    output = read_procfs()
    iface_list = regex.findall(output)

    if device in iface_list:
        return True
    else:
        return False


def diff_checks(first, second):
    diff = deepcopy(second)

    for k, v in first.iteritems():
        diff[k] -= v

    return diff


def calc_one_second(diff, interval):
    usage = {}

    for k, v in diff.iteritems():
        usage[k] = (v / 1024 ) / interval

    return usage


def check_iface(device, interval):
    first_check = iface_status(device)
    sleep(interval)
    second_check = iface_status(device)

    if first_check and second_check:
        diff = diff_checks(first_check, second_check)
        net_usage = calc_one_second(diff, interval)

        return net_usage
    else:
        return False


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description="""Icinga plugin to check
    network interfaces on Linux. Calculates network utilization in kB/s and
    packets per second. Generates an alert if values are greater than your
    thresholds.
    """)

    parser.add_argument('-w', '--warning', action='store', dest='warning_threshold', type=int, default=256,
        help='Warning threshold. Returns warning if interface transfer is greater than this value. Default is 256 kB/s.')
    parser.add_argument('-c', '--critical', action='store', dest='critical_threshold', type=int, default=512,
        help='Critical threshold. Returns critical if interface transfer is greater than this value. Default is 512 kB/s.')
    parser.add_argument('-i', '--interval', action='store', dest='interval', type=int, default=1,
        help='Time delay in seconds between collect networking information. Default is 1.')
    parser.add_argument('-d', '--device', action='store', dest='device', required=True, type=str,
        help='Network device name, ie: eth0, wlan1.')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
        help='No alert, only check interface and print performance data.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold
    interval = arguments.interval
    noalert = arguments.noalert
    device = arguments.device

    if warning > critical:
        print 'ERROR: warning threshold greater than critical threshold.'
        exit(UNKNOWN)

    if warning == critical:
        print 'ERROR: warning and critical threshold are equal.'
        exit(UNKNOWN)

    if valid_iface(device):
        iface_usage = check_iface(device, interval)

        if iface_usage:
            iface_usage['total_bytes'] = iface_usage['tx_bytes'] + iface_usage['rx_bytes']

            if iface_usage['total_bytes'] <= warning or noalert:
                print '%s %s TX %.2f kB/s RX %.2f kB/s, TX %.2f pkts/s RX %.2f pkts/s | %s' % (
                    device, 'OK', iface_usage['tx_bytes'],
                    iface_usage['rx_bytes'], iface_usage['tx_packets'],
                    iface_usage['rx_packets'], print_perfdata(iface_usage)
                    )
                exit(OK)

            if iface_usage['total_bytes'] > warning and iface_usage['total_bytes'] < critical:
                print '%s %s TX %.2f kB/s RX %.2f kB/s, TX %.2f pkts/s RX %.2f pkts/s | %s' % (
                    device, 'WARNING', iface_usage['tx_bytes'],
                    iface_usage['rx_bytes'], iface_usage['tx_packets'],
                    iface_usage['rx_packets'], print_perfdata(iface_usage)
                    )
                exit(WARNING)

            if iface_usage['total_bytes'] >= critical:
                print '%s %s TX %.2f kB/s RX %.2f kB/s, TX %.2f pkts/s RX %.2f pkts/s | %s' % (
                    device, 'CRITICAL', iface_usage['tx_bytes'],
                    iface_usage['rx_bytes'], iface_usage['tx_packets'],
                    iface_usage['rx_packets'], print_perfdata(iface_usage)
                    )
                exit(CRITICAL)
        else:
            print 'ERROR: Failed while get interface statistics'
            exit(UNKNOWN)
    else:
        print 'ERROR: %s is not a valid network interface.' % device
        exit(UNKNOWN)



if __name__ == '__main__':
    main()

