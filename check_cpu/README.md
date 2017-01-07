# check_cpu.py

## Description

Check CPU utilization on Linux systems.

Read /proc/stat file two times in a configurable interval, then calculates
CPU usage in percentage, generates an alert if total cpu usage (user + sys +
nice + steal + softirq + iowait + irq) is greater than your thresholds.

## Example

    $ check_cpu.py
    CPU OK 1.15% in use | 'softirq'=0.00 'iowait'=0.25 'sys'=0.15 'idle'=98.85 'user'=0.75 'irq'=0.00 'perc_inuse'=1.15 'total'=100.00 'steal'=0.00 'nice'=0.00

## Options

    -h, --help            show this help message and exit
    -w WARNING_THRESHOLD, --warning WARNING_THRESHOLD
                          Warning threshold. Returns warning if percentage of
                          CPU usage is greater than this value. Default is 80.
    -c CRITICAL_THRESHOLD, --critical CRITICAL_THRESHOLD
                          Critical threshold. Returns critical if percentage of
                          CPU usage is greater than this value. Default is 90.
    -i INTERVAL, --interval INTERVAL
                          Time delay in seconds between CPU info collects.
                          Default is 5.
    -n, --no-alert        No alert, only check CPU and print performance data.
    --version             show program's version number and exit
