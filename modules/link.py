#! /usr/bin/python

from utils.utils import Cmd, Logger
from modules.intf import Host, Switch
from modules.intf import Intf


logger = Logger('link.py', 'WARNING')

class Link:
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

        self.create()

    def create(self)
        cmd = ('ip link add {} type veth peer name {}').format(
               self.intf1.name, self.intf2.name)
        Cmd('safe', cmd)

        # append interface object to obj's intf list
        obj1.intf[self.intf1.name] = self.intf1
        obj2.intf[self.intf2.name] = self.intf2

    def append_to_host(self, obj, intf):
        assert type(obj) == Host
        
        cmd = 'ln -s /proc/{0}/ns/net /var/run/netns/{0}'.format(obj.pid)
        p = Cmd('safe', cmd)
        if p.stderr.strip() != '':
            logger.error('veth append to host error: %s' % p.stderr)

        cmd = 'ip link set {0} netns {1}'.format(intf.name, obj.pid)
        p = Cmd('safe', cmd)
        if p.stderr.strip() != '':
            logger.error('veth append to host error: %s' % p.stderr)

    def append_to_switch(self, obj, intf):
        assert type(obj) == Switch:

        cmd = 'ovs-vsctl add-port {0} {1}'.format(obj.name, intf.name)
        p = Cmd('safe', cmd)
        if p.stderr.strip() != '':
            logger.error('veth append to switch error: %s' % p.stderr)

