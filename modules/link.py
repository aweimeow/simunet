#! /usr/bin/python

from utils.utils import Cmd, Logger
from modules.node import Host, Switch
from modules.intf import Intf


logger = Logger('link.py', 'WARNING')

class Link(object):
    """ veth pair create by ip link """
    def __init__(self, obj1, obj2, intf1_name=None, intf2_name=None):
        self.obj1 = obj1
        self.obj2 = obj2

        # If intf name is not defined, 
        # default style is: h1-eth0, sw1-eth1
        # eth number start from 1 if obj is switch, else is 0
        self.intf1 = Intf(
            intf1_name if intf1_name else '%s-eth%s' % (
                obj1.name, len(obj1.intf) + 1 if type(obj1) is Switch else 0
                )
            )
        self.intf2 = Intf(
            intf2_name if intf2_name else '%s-eth%s' % (
                obj2.name, len(obj2.intf) + 1 if type(obj2) is Switch else 0
                )
            )

        self.create()

    def create(self):
        cmd = ('ip link add {} type veth peer name {}').format(
               self.intf1.name, self.intf2.name)
        Cmd('safe', cmd)

        # append interface object to obj's intf list
        self.obj1.intf[self.intf1.name] = self.intf1
        self.obj2.intf[self.intf2.name] = self.intf2

        if type(self.obj1) is Switch:
            self.append_to_switch(self.obj1, self.intf1)
        else:
            self.append_to_host(self.obj1, self.intf1)

        if type(self.obj2) is Switch:
            self.append_to_switch(self.obj2, self.intf2)
        else:
            self.append_to_host(self.obj2, self.obj2)

    def append_to_host(self, obj, intf):
        assert type(obj) is Host
        
        cmd = 'ln -s /proc/{0}/ns/net /var/run/netns/{0}'.format(obj.pid)
        p = Cmd('safe', cmd)
        if p.stderr.strip() != '':
            logger.error('veth append to host error: %s' % p.stderr)

        cmd = 'ip link set {0} netns {1}'.format(intf.name, obj.pid)
        p = Cmd('safe', cmd)
        if p.stderr.strip() != '':
            logger.error('veth append to host error: %s' % p.stderr)

    def append_to_switch(self, obj, intf):
        assert type(obj) is Switch

        cmd = 'ovs-vsctl add-port {0} {1}'.format(obj.name, intf.name)
        p = Cmd('safe', cmd)
        if p.stderr.strip() != '':
            logger.error('veth append to switch error: %s' % p.stderr)

class TCLink(Link):
    def __init__(self, obj1, obj2, intf1_name=None, intf2_name=None, 
                    bw=None, delay=None, loss=None):
        super(TCLink, self).__init__(obj1, obj2, intf1_name, intf2_name)
        self.bandwidth = bw
        self.delay = delay
        self.loss = loss

    def tc_active(self):
        cmds = []
        cmds.append('tc qdisc add dev %s root handle 5:0 htb default 1')
        if self.bandwidth:
            cmds.append('tc class add dev %s parent 5:0 ' + 
                'classid 5:1 htb rate %sMbit burst 15k' % self.bandwidth)
        if self.delay or self.loss:
            cmds.append('tc qdisc add dev %s parent 5:1 handle 10: ' +
                'netem delay %sms' % self.delay if self.delay else '' +
                'loss %s' % self.loss if self.loss else '')

        for cmd in cmds:
            if type(self.obj1) is Switch:
                p = Cmd('safe', cmd % self.intf1.name)
                if p.stderr:
                    logger.error('tc execute error: %s' % p.stderr)
            if type(self.obj2) is Switch:
                p = Cmd('safe', cmd % self.intf2.name)
                if p.stderr:
                    logger.error('tc execute error: %s' % p.stderr)

