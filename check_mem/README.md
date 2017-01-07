# check_mem.py

## Description

Check memory usage on Linux systems.

Reads `/proc/meminfo` file to calculate memory utilization in percentage,
generates an alert if value is greater than your thresholds. Cached and buffers
are counted as free memory.


## Usage

    $ check_mem.py
    Memory OK 12.58% in use | 'cached'=1851564.00 'total'=16342084.00 'buffers'=212180.00 'free'=12222520.00 'perc_inuse'=12.58


## Options

    -h, --help            show this help message and exit
    -w WARNING_THRESHOLD, --warning WARNING_THRESHOLD
                          Warning threshold. Returns warning if percentage of
                          memory usage is greater than this value. Default is
                          80.
    -c CRITICAL_THRESHOLD, --critical CRITICAL_THRESHOLD
                          Critical threshold. Returns critical if percentage of
                          memory usage is greater than this value. Default is
                          90.
    -n, --no-alert        No alert, only check memory and print performance
                          data.
    --version             show program's version number and exit


## Others

* [The /proc filesystem](https://www.kernel.org/doc/Documentation/filesystems/proc.txt)


