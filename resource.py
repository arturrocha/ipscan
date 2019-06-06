#!/usr/bin/python3
from __future__ import print_function
import socket
import time
import psutil
import platform
import subprocess


def is_connected(hostname):
    try:
        # see if we can resolve the host name -- tells us if there is
        # a DNS listening
        host = socket.gethostbyname(hostname)
        # connect to the host -- tells us if the host is actually
        # reachable
        s = socket.create_connection((host, 80), 2)
    except:
        return False
    return True


def loadavg():
    cmd = "cat /proc/loadavg | awk '{print $1}'"
    res = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True).communicate()[0]
    return float(res)
    
def Cpu():
    var = int(psutil.cpu_percent())
    return var


def Cpu_mac():
    cmd = "sysctl -n vm.loadavg"
    var = subprocess.Popen(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, shell=True).communicate()
    var = str(var[0]).split(' ')
    var1 = float(var[1])
    var2 = float(var[2])
    var3 = float(var[3])
    var = (((var1 * 100) + (var2 * 10) + var3) / 111)
    return var


def Mem():
    var = int(psutil.virtual_memory()[4])
    return var


def server_control(_type):
    plat = platform.system()
    msgctl = False
    if plat == 'Darwin':
        if _type == 'light':
            while Cpu_mac() > 4 or Mem() < 1000:
                time.sleep(3)
                if msgctl is False:
                    print('cpu = {}, free_mem = {}'.format(round(Cpu_mac(), 2), Mem()))
                    msgctl = True
                else:
                    pass
        elif _type == 'medium':
            while Cpu() > 8 or Mem() < 1000:
                time.sleep(2)
            print('cpu={}, free_mem={}'.format(round(Cpu_mac(), 2), Mem()))
        elif _type == 'heavy':
            while Cpu() > 8 or Mem() < 1000:
                time.sleep(2)
            print('cpu={}, free_mem={}'.format(round(Cpu_mac(), 2), Mem()))
    else:
        if _type == 'light':
            while Cpu() > 30 or Mem() < 1000:
                time.sleep(3)
            #print('server_control = {}, cpu > 30 = {} or free mem < 1000 = {}, sleep = {}'.format(_type, Cpu(), Mem(), 3))
        elif _type == 'medium':
            while Cpu() > 60 or Mem() < 1000:
                time.sleep(2)
        elif _type == 'heavy':
            while loadavg() > 4 or Mem() < 1000:
                print('{0}'.format(loadavg()))
                time.sleep(0.2)


def ip_increase(ip, mode):
    exp_ip = ip.split('.')
    exp_ip[3] = int(exp_ip[3])
    exp_ip[2] = int(exp_ip[2])
    exp_ip[1] = int(exp_ip[1])
    exp_ip[0] = int(exp_ip[0])
    exp_ip[3] += 1
    if exp_ip[3] == 256:
        exp_ip[3] = 0
        exp_ip[2] += 1
        if exp_ip[2] == 256:
            exp_ip[2] = 0
            exp_ip[1] += 1
            if exp_ip[1] == 256:
                exp_ip[1] = 0
                exp_ip[0] += 1
                if exp_ip[0] == 256:
                    exp_ip[0] = 0

    if mode == 'prod':
        # remove private and reserved
        # 0.0.0.0/8  Current network (only valid as source address)  RFC 6890
        if exp_ip[0] == 0:
            exp_ip[0] = 1
        # 10.0.0.0/8 Private network RFC 1918
        elif exp_ip[0] == 10:
            exp_ip[0] = 11
        # 100.64.0.0/10  Shared Address Space    RFC 6598
        elif exp_ip[0] == 100 and exp_ip[1] == 64:
            exp_ip[1] = 128
        # 127.0.0.0/8    Loopback    RFC 6890
        elif exp_ip[0] == 127:
            exp_ip[0] = 128
        # 169.254.0.0/16 Link-local  RFC 3927
        elif exp_ip[0] == 169 and exp_ip[1] == 254:
            exp_ip[1] = 255
        # 172.16.0.0/12  Private network RFC 1918
        elif exp_ip[0] == 172 and exp_ip[1] == 16:
            exp_ip[1] = 32
        # 192.0.0.0/24   IETF Protocol Assignments   RFC 6890
        elif exp_ip[0] == 192 and exp_ip[1] == 0 and exp_ip[2] == 0:
            exp_ip[2] = 1
        # 192.0.2.0/24   TEST-NET-1, documentation and examples  RFC 5737
        elif exp_ip[0] == 192 and exp_ip[1] == 0 and exp_ip[2] == 2:
            exp_ip[2] = 3
        # 192.88.99.0/24 IPv6 to IPv4 relay (includes 2002::/16) RFC 3068
        elif exp_ip[0] == 192 and exp_ip[1] == 88 and exp_ip[3] == 99:
            exp_ip[3] = 100
        # 192.168.0.0/16 Private network RFC 1918
        elif exp_ip[0] == 192 and exp_ip[1] == 168:
            exp_ip[1] = 169
        # 198.18.0.0/15  Network benchmark tests RFC 2544
        elif exp_ip[0] == 198 and exp_ip[1] == 18:
            exp_ip[1] = 20
            # 198.51.100.0/24    TEST-NET-2, documentation and examples  RFC 5737
        elif exp_ip[0] == 198 and exp_ip[1] == 51 and exp_ip[2] == 100:
            exp_ip[2] = 101
            # 203.0.113.0/24 TEST-NET-3, documentation and examples  RFC 5737
        elif exp_ip[0] == 203 and exp_ip[1] == 0 and exp_ip[2] == 113:
            exp_ip[2] = 114
        # 224.0.0.0/4    IP multicast (former Class D network)   RFC 5771
        # 240.0.0.0/4    Reserved (former Class E network)   RFC 1700
        # 255.255.255.255    Broadcast   RFC 919
        elif exp_ip[0] == 224:
            exp_ip[0] = 1
    else:
        pass

    return str(exp_ip[0]) + '.' + str(exp_ip[1]) + '.' + str(exp_ip[2]) + '.' + str(exp_ip[3])
