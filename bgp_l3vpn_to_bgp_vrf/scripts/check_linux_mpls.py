from lutil import luCommand, luLast
from lib import topotest
from lib.topolog import logger
minver = '4.9'
ret = luCommand('r1','apt-cache policy iproute2', 'Installed: ([\d\.]*)')
found = luLast()
dotest = -1
if ret != False and found != None:
    dotest = topotest.version_cmp(found.group(1), minver)
if dotest == -1:
    luCommand('r1','apt-cache policy iproute2', '.', 'pass', 'Skipping test, iproute2 version {} < {}'.format(found.group(1), minver))
    ret = False
else:
    logger.info('iproute2 ver = {} dotest = {}'.format(found.group(1), dotest))
    ret = luCommand('r2','ip -M route show','\d*(?= via inet 10.0.2.4 dev r2-eth1)','wait','See mpls route to r4')
    found = luLast()
if ret != False and found != None:
    label4r4 = found.group(0)
    luCommand('r2','ip -M route show','.','pass','See %s as label to r4' % label4r4)
    ret = luCommand('r2','ip -M route show','\d*(?= via inet 10.0.1.1 dev r2-eth0)','wait','See mpls route to r1')
    found = luLast()
if ret != False and found != None:
    label4r1 = found.group(0)
    luCommand('r2','ip -M route show','.','pass','See %s as label to r1' % label4r1)
    luCommand('ce4','ip route add default via 192.168.2.1')
    luCommand('ce1','ip route add default via 192.168.1.1')
    luCommand('r1','ip route add 99.0.0.1 vrf cust1 dev r1-eth4 via 192.168.1.2')
    luCommand('r4','ip route add 99.0.0.4 vrf cust2 dev r4-eth4 via 192.168.2.2')
    luCommand('r1','ip -M route add 101 dev cust1')
    luCommand('r4','ip -M route add 104 dev cust2')
    luCommand('r1','ip route add 99.0.0.4/32 vrf cust1 nexthop encap mpls %s/104 via 10.0.1.2 dev r1-eth0'%label4r4)
    luCommand('r4','ip route add 99.0.0.1/32 vrf cust2 nexthop encap mpls %s/101 via 10.0.2.2 dev r4-eth0'%label4r1)
    luCommand('r1','ip route show vrf cust1','99.0.0.4','pass', 'VRF->MPLS PHP route installed')
    luCommand('r4','ip route show vrf cust2','99.0.0.1','pass', 'VRF->MPLS PHP route installed')
    luCommand('r1','ip -M route show','101','MPLS->VRF route installed')
    luCommand('r4','ip -M route show','104','MPLS->VRF route installed')
    luCommand('ce1','ping 99.0.0.4 -I 99.0.0.1 -c 1',' 0. packet loss','wait','CE->CE (loopback) ping - l3vpn+zebra case')
    luCommand('ce4','ping 99.0.0.1 -I 99.0.0.4 -c 1',' 0. packet loss','wait','CE->CE (loopback) ping - l3vpn+zebra case')
    luCommand('r1','ip route del 99.0.0.4/32 vrf cust1')
    luCommand('r4','ip route del 99.0.0.1/32 vrf cust2')
    luCommand('r1','ip route add 99.0.0.4/32 vrf cust1 nexthop encap mpls %s/1004/104 via 10.0.1.2 dev r1-eth0'%label4r4)
    luCommand('r4','ip -M route add 1004 dev lo')
    luCommand('r4','ip route add 99.0.0.1/32 vrf cust2 nexthop encap mpls %s/1001/101 via 10.0.2.2 dev r4-eth0'%label4r1)
    luCommand('r1','ip -M route add 1001 dev lo')
    luCommand('r1','ip route show vrf cust1','99.0.0.4.*1004/104','pass', 'VRF->MPLS non-PHP route installed')
    luCommand('r4','ip route show vrf cust2','99.0.0.1.*1001/101','pass', 'VRF->MPLS non-PHP route installed')
    luCommand('r1','ip -M route show','1001','MPLS "non-PHP" route installed')
    luCommand('r4','ip -M route show','1004','MPLS "non-PHP" route installed')
    luCommand('ce1','ping 99.0.0.4 -I 99.0.0.1 -c 1',' 0. packet loss','wait','CE->CE (loopback) ping')
    luCommand('ce4','ping 99.0.0.1 -I 99.0.0.4 -c 1',' 0. packet loss','wait','CE->CE (loopback) ping')
