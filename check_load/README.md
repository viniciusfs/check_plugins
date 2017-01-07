# check_load.py

## Description

Reads `/proc/loadavg` file and generate an alert if load1 value is greater
than your thresholds.


## Usage

    $ check_load.py
    Load average OK 0.07, 0.18, 0.30 | 'load1'=0.07 'load15'=0.30 'load5'=0.18

    $ check_load.py -w 1.5 -c 4
    Load average WARNING 2.39, 0.96, 0.60 | 'load1'=2.39 'load15'=0.60 'load5'=0.96

    $ check_load.py -w 1.5 -c 4 --cpu-count
    Load average OK 2.44, 0.99, 0.62 | 'load1'=2.44 'load15'=0.62 'load5'=0.99


## Options

	-h, --help            show this help message and exit
	-w WARNING_THRESHOLD, --warning WARNING_THRESHOLD
							Warning threshold. Returns warning if load1 is greater
							than this value. Default is 1.
	-c CRITICAL_THRESHOLD, --critical CRITICAL_THRESHOLD
							Critical threshold. Returns critical if load1 is
							greater than this value. Default is 2.
	--cpu-count           Divides load per CPU count before test against
							thresholds.
	-n, --no-alert        No alert, only check and print performance data.
	--version             show program's version number and exit


## FIXME

- [ ] Update all keys in load_average dict when cpucount is true
