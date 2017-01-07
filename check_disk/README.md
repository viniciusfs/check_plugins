# check_disk.py

## Description

Check file system utilization on Linux systems.

Read `/proc/mounts` to get list of valid mount points. Gets information about
specified mount point using os.statvfs module. Calculates file system
utilization and generates an alarm if values are greater than your threhsold.


## Usage

    $ check_disk.py --mount-point /home
    File system /home OK 41.63% in use | 'total'=921409500.00 'free'=537809192.00 'used'=336772380.00 'perc_inuse'=41.63

    $ check_disk.py --mount-point=/ssd_data -w 85 -c 90
    File system /ssd_data CRITICAL 90.12% in use | 'total'=182130892.00 'free'=17998916.00 'used'=154857200.00 'perc_inuse'=90.12


## Options

    -h, --help            show this help message and exit
    -w WARNING_THRESHOLD, --warning WARNING_THRESHOLD
                          Warning threshold. Returns warning if percentage of
                          used space is greater than this value. Default is 80.
    -c CRITICAL_THRESHOLD, --critical CRITICAL_THRESHOLD
                          Critical threshold. Returns critical if percentage of
                          used space is greater than this value. Default is 90.
    -m MOUNT_POINT, --mount-point MOUNT_POINT
                          Mount point to be checked.
    -n, --no-alert        No alert, only check and print performance data.
    --version             show program's version number and exit
