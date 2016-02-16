# check_plugins

A collection of Icinga plugins for Linux server monitoring.

* check_cpu.py
* check_disk.py
* check_load.py
* check_mem.py
* check_network.py
* check_swap.py


## check_cpu.py

    $ check_cpu.py 
    CPU OK 1.15% in use | 'softirq'=0.00 'iowait'=0.25 'sys'=0.15 'idle'=98.85 'user'=0.75 'irq'=0.00 'perc_inuse'=1.15 'total'=100.00 'steal'=0.00 'nice'=0.00 


## check_disk.py

    $ check_disk.py --mount-point /home
    File system /home OK 41.63% in use | 'total'=921409500.00 'free'=537809192.00 'used'=336772380.00 'perc_inuse'=41.63 


## check_load.py

    $ check_load.py 
    Load average OK 0.07, 0.18, 0.30 | 'load1'=0.07 'load15'=0.30 'load5'=0.18 


## check_mem.py

    $ check_mem.py 
    Memory OK 12.58% in use | 'cached'=1851564.00 'total'=16342084.00 'buffers'=212180.00 'free'=12222520.00 'perc_inuse'=12.58 


## check_network.py

    $ check_network.py --device eth0
    eth0 OK TX 13.24 kB/s RX 2.39 kB/s, TX 0.01 pkts/s RX 0.02 pkts/s | 'rx_multicast'=0.00 'rx_packets'=0.02 'rx_compressed'=0.00 'rx_bytes'=2.39 'rx_errs'=0.00 'rx_fifo'=0.00 'tx_fifo'=0.00 'rx_frame'=0.00 'total_bytes'=15.63 'tx_colls'=0.00 'tx_drop'=0.00 'tx_bytes'=13.24 'tx_errs'=0.00 'tx_packets'=0.01 'tx_compressed'=0.00 'rx_drop'=0.00 


## check_swap.py

    $ check_swap.py 
    Swap OK 0.00% in use | 'total'=8294396.00 'used'=0.00 'perc_inuse'=0.00 'free'=8294396.00 

