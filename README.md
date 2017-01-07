# Python check_plugins

A collection of check plugins for monitoring written in Python.


## Purporse and motivation

While deploying a Icinga server I thought was a good idea write my own check
plugins as a programming exercise. To make it a little harder (or not
:satisfied:) all plugins must be written in Python only without external tools.


## Plugin list

* [check_cpu.py](./check_cpu/README.md)
* [check_disk.py](./check_disk/README.md)
* [check_load.py](./check_load/README.md)
* [check_mem.py](./check_mem/README.md)
* [check_network.py](./check_network/README.md)
* [check_swap.py](./check_swap/README.md)


## Specification

The specification for check plugins are mostly the same used for
[Icinga](https://icinga.org), [Nagios](https://nagios.org) and
[Sensu](https://sensuapp.org) plugins.

### Exit code

The exit status of check plugins are treated as follows:

| exit status | meaning |
|-------------|---------|
| 0 | OK |
| 1 | WARNING |
| 2 | CRITICAL |
| 3 | UNKNOWN |

### Performance data

In addition to normal status data the check plugins returns performance data.
Performance data can be passed from Icinga or Nagios to external applications,
usually to plot nice charts and create monitoring dashboards.

### Safe defaults

When possible, the check plugins can be run successfully without any argument,
thanks to built in safe defaults.


## Authors

  - Vinícius Figueiredo <viniciusfs@gmail.com>


## License

    The MIT License (MIT)

    Copyright (c) 2017 Vinícius Figueiredo

    Permission is hereby granted, free of charge, to any person obtaining a copy of
    this software and associated documentation files (the "Software"), to deal in
    the Software without restriction, including without limitation the rights to
    use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
    the Software, and to permit persons to whom the Software is furnished to do so,
    subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
    FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
    COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
    IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
    CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

