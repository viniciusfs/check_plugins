#!/usr/bin/env python

"""
This file is part of viniciusfs check_plugins project
http://github.com/viniciusfs/check_plugins

This file has code from:
http://voorloopnul.com/blog/a-python-netstat-in-less-than-100-lines-of-code
"""

import pwd
import os
import re
import glob
import argparse

OK = 0
WARNING = 1
CRITICAL = 2
UNKNOWN = 3

PROC_TCP4 = "/proc/net/tcp"
PROC_UDP4 = "/proc/net/udp"
PROC_TCP6 = "/proc/net/tcp6"
PROC_UDP6 = "/proc/net/udp6"
PROC_PACKET = "/proc/net/packet"
TCP_STATE = {
        '01':'ESTABLISHED',
        '02':'SYN_SENT',
        '03':'SYN_RECV',
        '04':'FIN_WAIT1',
        '05':'FIN_WAIT2',
        '06':'TIME_WAIT',
        '07':'CLOSE',
        '08':'CLOSE_WAIT',
        '09':'LAST_ACK',
        '0A':'LISTEN',
        '0B':'CLOSING'
        }


def _tcp4load():
    ''' Read the table of tcp connections & remove the header  '''
    with open(PROC_TCP4,'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def _tcp6load():
    ''' Read the table of tcpv6 connections & remove the header'''
    with open(PROC_TCP6,'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def _udp4load():
    '''Read the table of udp connections & remove the header '''
    with open(PROC_UDP4,'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def _udp6load():
    '''Read the table of udp connections & remove the header '''
    with open(PROC_UDP6,'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def _packetload():
    ''' Read the contents of /proc/net/packet for finding processes with packet sockets '''
    with open(PROC_PACKET,'r') as f:
        content = f.readlines()
        content.pop(0)
    return content


def _hex2dec(s):
    return str(int(s,16))


def _ip(s):
    ip = [(_hex2dec(s[6:8])),(_hex2dec(s[4:6])),(_hex2dec(s[2:4])),(_hex2dec(s[0:2]))]
    return '.'.join(ip)


def _ip6(s):
    #this may need to be converted to a string to work properly.
    ip = [s[6:8],s[4:6],s[2:4],s[0:2],s[12:14],s[14:16],s[10:12],s[8:10],s[22:24],s[20:22],s[18:20],s[16:18],s[30:32],s[28:30],s[26:28],s[24:26]]
    return ':'.join(ip)


def _remove_empty(array):
    return [x for x in array if x !='']


def _convert_ipv4_port(array):
    host,port = array.split(':')
    return _ip(host),_hex2dec(port)


def _convert_ipv6_port(array):
    host,port = array.split(':')
    return _ip6(host),_hex2dec(port)


def netstat_tcp4():
    '''
    Function to return a list with status of tcp connections on Linux systems.
    Please note that in order to return the pid of of a network process running on the
    system, this script must be ran as root.
    '''

    tcpcontent =_tcp4load()
    tcpresult = []
    for line in tcpcontent:
        line_array = _remove_empty(line.split(' '))     # Split lines and remove empty spaces.
        l_host,l_port = _convert_ipv4_port(line_array[1]) # Convert ipaddress and port from hex to decimal.
        r_host,r_port = _convert_ipv4_port(line_array[2])
        tcp_id = line_array[0]
        state = TCP_STATE[line_array[3]]
        uid = pwd.getpwuid(int(line_array[7]))[0]       # Get user from UID.
        inode = line_array[9]                           # Need the inode to get process pid.
        pid = _get_pid_of_inode(inode)                  # Get pid prom inode.
        try:                                            # try read the process name.
            exe = os.readlink('/proc/'+pid+'/exe')
        except:
            exe = None

        nline = [tcp_id, uid, l_host+':'+l_port, r_host+':'+r_port, state, pid, exe]
        tcpresult.append(nline)
    return tcpresult


def netstat_tcp6():
    '''
    This function returns a list of tcp connections utilizing ipv6. Please note that in order to return the pid of of a
    network process running on the system, this script must be ran as root.
    '''
    tcpcontent = _tcp6load()
    tcpresult = []
    for line in tcpcontent:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = _convert_ipv6_port(line_array[1])
        r_host,r_port = _convert_ipv6_port(line_array[2])
        tcp_id = line_array[0]
        state = TCP_STATE[line_array[3]]
        uid = pwd.getpwuid(int(line_array[7])) [0]
        inode = line_array[9]
        pid = _get_pid_of_inode(inode)
        try:                                            # try read the process name.
            exe = os.readlink('/proc/'+pid+'/exe')
        except:
            exe = None

        nline = [tcp_id, uid, l_host+':'+l_port, r_host+':'+r_port, state, pid, exe]
        tcpresult.append(nline)
    return tcpresult


def netstat_udp4():
    '''
    Function to return a list with status of udp connections on Linux systems. Please note that UDP is stateless, so
    state will always be blank. Please note that in order to return the pid of of a network process running on the
    system, this script must be ran as root.
    '''

    udpcontent =_udp4load()
    udpresult = []
    for line in udpcontent:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = _convert_ipv4_port(line_array[1])
        r_host,r_port = _convert_ipv4_port(line_array[2])
        udp_id = line_array[0]
        udp_state ='Stateless' #UDP is stateless
        uid = pwd.getpwuid(int(line_array[7]))[0]
        inode = line_array[9]
        pid = _get_pid_of_inode(inode)
        try:
            exe = os.readlink('/proc/'+pid+'/exe')
        except:
            exe = None

        nline = [udp_id, uid, l_host+':'+l_port, r_host+':'+r_port, udp_state, pid, exe]
        udpresult.append(nline)
    return udpresult


def netstat_udp6():
    '''
    Function to return a list of udp connection utilizing ipv6. Please note that UDP is stateless, so state will always
    be blank. Please note that in order to return the pid of of a network process running on the system, this script
    must be ran as root.
    '''

    udpcontent =_udp6load()
    udpresult = []
    for line in udpcontent:
        line_array = _remove_empty(line.split(' '))
        l_host,l_port = _convert_ipv6_port(line_array[1])
        r_host,r_port = _convert_ipv6_port(line_array[2])
        udp_id = line_array[0]
        udp_state ='Stateless' #UDP is stateless
        uid = pwd.getpwuid(int(line_array[7]))[0]
        inode = line_array[9]
        pid = _get_pid_of_inode(inode)
        try:
            exe = os.readlink('/proc/'+pid+'/exe')
        except:
            exe = None

        nline = [udp_id, uid, l_host+':'+l_port, r_host+':'+r_port, udp_state, pid, exe]
        udpresult.append(nline)
    return udpresult


def packet_socket():
    '''
    Function to return a list of pids and process names utilizing packet sockets.
    '''

    packetcontent = _packetload()
    packetresult = []
    for line in packetcontent:
        line_array = _remove_empty(line.split(' '))
        inode = line_array[8].rstrip()
        pid = _get_pid_of_inode(inode)
        try:
            exe = os.readlink('/proc/'+pid+'/exe')
        except:
            exe = None

        nline = [pid, exe]
        packetresult.append(nline)
    return packetresult


def _get_pid_of_inode(inode):
    '''
    To retrieve the process pid, check every running process and look for one using
    the given inode.
    '''
    for item in glob.glob('/proc/[0-9]*/fd/[0-9]*'):
        try:
            if re.search(inode,os.readlink(item)):
                return item.split('/')[2]
        except:
            pass
    return None


def ipv4toipv6(ipv4):
    numbers = ipv4.split('.')
    ipv6 = '00:00:00:00:00:00:00:00:00:00:FF:FF:' + '{0:02X}:{1:02X}:{2:02X}:{3:02X}'.format(int(numbers[0]), int(numbers[1]), int(numbers[2]), int(numbers[3]))
    return ipv6


def print_debug():
    print "\nLegend: Connection ID, UID, localhost:localport, remotehost:remoteport, state, pid, exe name"
    print "\nTCP (v4) Results:\n"
    for conn_tcp in netstat_tcp4():
        print conn_tcp
    print "\nTCP (v6) Results:\n"
    for conn_tcp6 in netstat_tcp6():
        print conn_tcp6
    print "\nUDP (v4) Results:\n"
    for conn_udp in netstat_udp4():
        print conn_udp
    print "\nUDP (v6) Results:\n"
    for conn_udp6 in netstat_udp6():
        print conn_udp6
    print "\nPacket Socket Results:\n"
    for pack_sock in packet_socket():
        print pack_sock


def check_netstat(dhost, dport):
    results = { 'connections': 0, 'established': 0, 'syn_sent': 0,
                'syn_recv': 0, 'fin_wait1': 0, 'fin_wait2': 0,
                'time_wait': 0, 'close': 0, 'close_wait': 0,
                'last_ack': 0, 'listen': 0, 'closing': 0 }

    tcp4 = netstat_tcp4()
    connections = tcp4 + netstat_tcp6()

    destination = '%s:%d' % (dhost, dport)
    destination_ipv6 = '%s:%d' % (ipv4toipv6(dhost), dport)

    for connection in connections:
        source, target, state = connection[2], connection[3], connection[4]

        if target == destination or target == destination_ipv6:
            results['connections'] += 1

            if state == 'ESTABLISHED':
                results['established'] += 1

            if state == 'SYN_SENT':
                results['syn_sent'] += 1

            if state == 'SYN_RECV':
                results['syn_recv'] += 1

            if state == 'FIN_WAIT1':
                results['fin_wait1'] += 1

            if state == 'FIN_WAIT2':
                results['fin_wait2'] += 1

            if state == 'TIME_WAIT':
                results['time_wait'] += 1

            if state == 'CLOSE':
                results['close'] += 1

            if state == 'CLOSE_WAIT':
                results['close_wait'] += 1

            if state == 'LAST_ACK':
                results['last_ack'] += 1

            if state == 'LISTEN':
                results['listen'] += 1

            if state == 'CLOSED':
                results['closed'] += 1

    return results


def print_perfdata(results):
    output = ''

    for k, v in results.iteritems():
        output += '\'%s\'=%.2f ' % (k, v)

    return output


def main():
    parser = argparse.ArgumentParser(description='Icinga plugin to check network connections on Linux using /proc/net.')

    parser.add_argument('--min', action='store', dest='minimal', type=int, default=1,
            help='Alerts critical state if connection number is bellow this minimal number.')
    parser.add_argument('--max', action='store', dest='maximum', type=int, default=2,
            help='Alerts critical state if connection number is above this maximum number.')
    parser.add_argument('-H', '--host', action='store', dest='host', type=str, help='Target host network address.')
    parser.add_argument('-p', '--port', action='store', dest='port', type=int, help='Target host port number.')
    parser.add_argument('-d', '--debug', action='store_true', dest='debug')
    parser.add_argument('-n', '--no-alert', action='store_true', dest='noalert',
            help='No alert, only check network status and print performance data.')
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.1')

    arguments = parser.parse_args()

    minimal = arguments.minimal
    maximum = arguments.maximum
    dhost = arguments.host
    dport = arguments.port
    noalert = arguments.noalert
    debug = arguments.debug

    if debug:
	print_debug()
	exit(OK)

    if minimal > maximum:
        print 'ERROR: minimal threshold greater than maximum threshold.'
        exit(UNKNOWN)

    results = check_netstat(dhost, dport)

    if results:
        if noalert:
            print 'Netstat %s %d established connection(s) to %s:%d | %s' % ('OK', results['established'], dhost, dport, print_perfdata(results))
            exit(OK)

        if results['established'] < minimal:
            print 'Netstat %s %d established connection(s) to %s:%d | %s' % ('CRITICAL', results['established'], dhost, dport, print_perfdata(results))
            exit(CRITICAL)

        if results['established'] >= minimal and results['established'] <= maximum:
            print 'Netstat %s %d established connection(s) to %s:%d | %s' % ('OK', results['established'], dhost, dport, print_perfdata(results))
            exit(OK)

        if results['established'] > maximum:
            print 'Netstat %s %d established connections to %s:%d | %s' % ('CRITICAL', results['established'], dhost, dport, print_perfdata(results))
            exit(CRITICAL)


if __name__ == '__main__':
    main()

