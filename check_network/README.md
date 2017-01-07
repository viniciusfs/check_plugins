# check_network.py

## Description

Check network utilization on Linux systems.

Reads `/proc/net/dev` file two times in a configurable interval, then
calculates network utilization in kB/s and packets per second. Generates an
alert if values are greater than your thresholds.


## Usage

    $ check_network.py --device eth0
    eth0 OK TX 13.24 kB/s RX 2.39 kB/s, TX 0.01 pkts/s RX 0.02 pkts/s | 'rx_multicast'=0.00 'rx_packets'=0.02 'rx_compressed'=0.00 'rx_bytes'=2.39 'rx_errs'=0.00 'rx_fifo'=0.00 'tx_fifo'=0.00 'rx_frame'=0.00 'total_bytes'=15.63 'tx_colls'=0.00 'tx_drop'=0.00 'tx_bytes'=13.24 'tx_errs'=0.00 'tx_packets'=0.01 'tx_compressed'=0.00 'rx_drop'=0.00


## Options

    -h, --help            show this help message and exit
    -w WARNING_THRESHOLD, --warning WARNING_THRESHOLD
                          Warning threshold. Returns warning if interface
                          transfer is greater than this value. Default is 256
                          kB/s.
    -c CRITICAL_THRESHOLD, --critical CRITICAL_THRESHOLD
                          Critical threshold. Returns critical if interface
                          transfer is greater than this value. Default is 512
                          kB/s.
    -i INTERVAL, --interval INTERVAL
                          Time delay in seconds between collect networking
                          information. Default is 1.
    -d DEVICE, --device DEVICE
                          Network device name, ie: eth0, wlan1.
    -n, --no-alert        No alert, only check interface and print performance
                          data.
    --version             show program's version number and exit


## Others

* [The /proc filesystem](https://www.kernel.org/doc/Documentation/filesystems/proc.txt)
