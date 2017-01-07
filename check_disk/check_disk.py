#!/usr/bin/env python

"""
Icinga plugin to check file system utilization on Linux systems. This is a pure
Python plugin, works with Python 2.6.x (requires argparse) and Python 2.7.x.
Tested on CentOS 7, CentOS 6 and Ubuntu 15.

It reads /proc/mounts to get list of valid mount points. Gets information about
specified mount point using os.statvfs module. Calculates file system
utilization and generates an alarm if values are greater than your threhsold.

Example:
    $ check_disk.py --mount-point /home
    File system /home OK 46.27% in use | 'total'=921409500.00 'free'=495051108.00 'used'=379530464.00 'perc_inuse'=46.27

Project Page: http://www.ultrav.com.br/projetos/check-plugins/
Author: Vinicius Figueiredo <viniciusfs@gmail.com>
Version: 0.1.1

Change log:
  - 0.1.1 - Jan 31 2016 - Small fixes and cosmetic changes.
  - 0.1   - Jan 30 2016 - First usable version.
"""

import argparse
import os

from sys import exit


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def read_procfs():
    try:
        with open('/proc/mounts', 'r') as data_file:
            contents = data_file.read()

            return contents

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKNOWN)


def disk_status(mount_point):
    try:
        stat = os.statvfs(mount_point)

    except OSError as e:
        print 'ERROR: Error while getting disk information.'
        exit(UNKNOWN)

    total = float((stat.f_blocks * stat.f_frsize) / 1024)
    used = float(((stat.f_blocks - stat.f_bfree) * stat.f_frsize) / 1024)
    free = float((stat.f_bavail * stat.f_frsize) / 1024)
    perc_inuse = 100 - (free / total) * 100

    status = {
        'total': total,
        'used': used,
        'free': free,
        'perc_inuse': perc_inuse
    }

    return status


def valid_mount_point(mount_point):
    valid_mounts = []
    exclude_fstypes = [ 'sysfs', 'proc', 'devtmpfs', 'devpts', 'tmpfs',
        'securityfs', 'cgroup', 'efivarfs', 'autofs', 'debugfs', 'mqueue',
        'hugetlbfs', 'fusectl', 'rpc_pipefs', 'nfsd', 'binfmt_misc',
        'fuse.gvfsd-fuse', 'pstore' ]
    output = read_procfs()

    for line in output[:-1].split('\n'):
        device, mount, fstype = line.split()[0], line.split()[1], line.split()[2]

        if fstype not in exclude_fstypes:
            valid_mounts.append(mount)

    if mount_point in valid_mounts:
        return True
    else:
        return False


def check_disk(mount_point):
    disk_usage = disk_status(mount_point)

    return disk_usage


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description="""Icinga plugin to check
    the amount of used file system space on Linux. It generates an alert if
    percentage of used space is greater then your thresholds. Performance
    data output in kB.
    """)

    parser.add_argument('-w', '--warning', action='store', dest='warning_threshold', type=int, default=80,
        help='Warning threshold. Returns warning if percentage of used space is greater than this value. Default is 80.')
    parser.add_argument('-c', '--critical', action='store', dest='critical_threshold', type=int, default=90,
        help='Critical threshold. Returns critical if percentage of used space is greater than this value. Default is 90.')
    parser.add_argument('-m', '--mount-point', action='store', dest='mount_point',
        required=True, type=str, help='Mount point to be checked.')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
        help='No alert, only check and print performance data.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.1')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold
    mount_point = arguments.mount_point
    noalert = arguments.noalert

    if warning > critical:
        print 'ERROR: warning threshold greater than critical threshold.'
        exit(UNKNOWN)

    if warning == critical:
        print 'ERROR: warning and critical threshold are equal.'
        exit(UNKNOWN)

    if valid_mount_point(mount_point):
        disk_usage = check_disk(mount_point)
    else:
        print 'ERROR: %s is not a valid mount point.' % mount_point
        exit(UNKNOWN)

    if disk_usage['perc_inuse'] <= warning or noalert:
        print 'File system %s %s %.2f%% in use | %s' % (mount_point, 'OK', disk_usage['perc_inuse'], print_perfdata(disk_usage))
        exit(OK)

    if disk_usage['perc_inuse'] > warning and disk_usage['perc_inuse'] < critical:
        print 'File system %s %s %.2f%% in use | %s' % (mount_point, 'WARNING', disk_usage['perc_inuse'], print_perfdata(disk_usage))
        exit(WARNING)

    if disk_usage['perc_inuse'] >= critical:
        print 'File system %s %s %.2f%% in use | %s' % (mount_point, 'CRITICAL', disk_usage['perc_inuse'], print_perfdata(disk_usage))
        exit(CRITICAL)



if __name__ == '__main__':
    main()

