#!/usr/bin/env python

"""
Icinga plugin to check the amount of used file system space on Linux.

Author: Vinicius Figueiredo <viniciusfs@gmail.com>
"""


import argparse
import os

from sys import exit


OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3



def valid_mount_point(mount_point):
    valid_mounts = []

    exclude_fstypes = [ 'sysfs', 'proc', 'devtmpfs', 'devpts', 'tmpfs',
        'securityfs', 'cgroup', 'efivarfs', 'autofs', 'debugfs', 'mqueue',
        'hugetlbfs', 'fusectl', 'rpc_pipefs', 'nfsd', 'binfmt_misc',
        'fuse.gvfsd-fuse', 'pstore' ]

    try:
        with open('/proc/mounts', 'r') as mount_file:
            for line in mount_file.readlines():
                device, mount, fstype = line.split()[0], line.split()[1], line.split()[2]

                if fstype not in exclude_fstypes:
                    valid_mounts.append(mount)

    except IOError as e:
        print 'ERROR: %s' % e
        exit(UNKOWN)

    if mount_point in valid_mounts:
        return True
    else:
        return False


def check_disk(mount_point):
    status = os.statvfs(mount_point)

    total = float((status.f_blocks * status.f_frsize) / 1024)
    used = float(((status.f_blocks - status.f_bfree) * status.f_frsize) / 1024)
    free = float((status.f_bavail * status.f_frsize) / 1024)

    perc_inuse = 100 - (free / total) * 100
    disk_usage = {
        'total': total,
        'used': used,
        'free': free,
        'perc_inuse': perc_inuse
    }

    return disk_usage


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description='Icinga plugin to check the amount of used file system space on Linux.')

    parser.add_argument('-w', action='store', dest='warning_threshold', type=int, default=80,
        help='Warning threshold. Returns warning if percentage of used space is greater than this value. Default is 80.')
    parser.add_argument('-c', action='store', dest='critical_threshold', type=int, default=90,
        help='Critical threshold. Returns critical if percentage of used space is greater than this value. Default is 90.')
    parser.add_argument('-m', '--mount-point', action='store', dest='mount_point', required=True, type=str, help='Mount point to be checked.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1')

    arguments = parser.parse_args()

    warning = arguments.warning_threshold
    critical = arguments.critical_threshold
    mount_point = arguments.mount_point

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

    if disk_usage['perc_inuse'] <= warning:
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

