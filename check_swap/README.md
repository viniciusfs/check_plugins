# check_swap.py

## Description

Check swap utilization on Linux systems.

Reads `/proc/meminfo` file to calculate swap utilization in percentage,
generates an alert if value is greater than your thresholds.


## Usage

    $ check_swap.py
    Swap OK 0.00% in use | 'total'=8294396.00 'used'=0.00 'perc_inuse'=0.00 'free'=8294396.00


## Options

    -h, --help            show this help message and exit
    -w WARNING_THRESHOLD, --warning WARNING_THRESHOLD
                          Warning threshold. Returns warning if percentage of
                          swap usage is greater than this value. Default is 80.
    -c CRITICAL_THRESHOLD, --critical CRITICAL_THRESHOLD
                          Critical threshold. Returns critical if percentage of
                          swap usage is greater than this value. Default is 90.
    -n, --no-alert        No alert, only check swap and print performance data.
    --version             show program's version number and exit

## Others

* [The /proc filesystem](https://www.kernel.org/doc/Documentation/filesystems/proc.txt)

