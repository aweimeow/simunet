#! /usr/bin/python
# -*- encoding: utf-8 -*-

import logging

from modules.interface import Intf
from utils.utils import Cmd, Logger

logger = Logger('node.py', 'WARNING')


class Host:
    """
    A docker based container, use to simulate network host
    """

    def __init__(self, name, ip, mac=None, os='ubuntu:14.04'):
        """default value:
        name: h1 (str)
        ip: 10.0.0.1/24 (str)
        os: ubuntu:14.04 (str)
        mac: AA:BB:CC:DD:EE:FF (str)
        """

        self.os = os
        self.name = name
        self.ip = ip
        self.mac = mac
        self.gateway = None
        self.status = None
        self.create()

    def set_intf(self, intf):
        self.intf = intf

    def set_gateway(self, gateway):
        self.gateway = gateway

    def network_config(self):
        """ Configuration for container's IP, mac and gateway """

        cmd = ("docker exec %s ifconfig %s-eth0 %s").format(
               self.name, self.name, self.ip)
        Cmd('safe', cmd)

        if self.mac:
           cmd = ("docker exec %s ifconfig %s-eth0 hw ether %s").format(
                   self.name, self.name, self.ip, self.mac)

        if self.gateway:
            cmd = ("docker exec %s route add default gw %s").format(
                   self.name, self.gateway)
            Cmd('safe', cmd)

    def create(self):
        """ Create Container """

        cmd = ("docker create --net='none' --name='{}'"
               " --privileged -it {}").format(self.name, self.os)
        p = Cmd('safe', cmd)
        if p.stdout.strip() == '':
            logmsg = "Can't create Container %s: %s" % (self.name, p.stderr)
            logger.warn(logmsg)
        else:
            self.container_id = p.stdout.strip()
            logger.info('%s Created: %s' % (self.name, self.container_id))
            self.status = 'create'

    def start(self):
        """ Start the container """

        if self.status == 'start':
            logger.error('%s has been started.' % self.name)
            return

        # Send start command
        cmd = "docker start {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.status = 'start'

        # get docker's pid
        cmd = "docker inspect --format '{{.State.Pid}}' %s" % self.name
        p = Cmd('safe', cmd)
        self.pid = p.stdout.strip()

    def stop(self):
        """ Stop the container """

        if self.status == 'stop':
            logger.error('%s has been stoped.' % self.name)
            return

        cmd = "docker stop {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.status = 'stop'

    def destroy(self):
        """ Remove this Container """

        if self.status == 'destroy':
            logger.error('%s has been destroyed.' % self.name)
            return

        if self.status == 'start':
            logger.warn('%s can\'t destroy: Stop container first' % self.name)
            return

        cmd = "docker rm {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.status = 'destroy'


class Switch:
    """ ovs simulated switch """

    def __init__(self, name):
        
        self.intf = []

        # Name Check for command injection
        if " " in name or ";" in name:
            logger.error('"%s" cannot be Switch name.' % name)
            return
        else:
            self.name = name
            self.create()

    def create(self):
        cmd = "ovs-vsctl add-br %s" % self.name
        p = Cmd('safe', cmd)

        if p.stderr:
            logger.error('Switch %s Create Error: %s' % (self.name, p.stderr))

    def destroy(self):
        cmd = "ovs-vsctl del-br %s" % self.name
        p = Cmd('safe', cmd)

        if p.stderr:
            logger.error

    def set_intf(self, intf):
        if type(intf) is Intf:
            if not intf in self.intf:
                self.intf.append(intf)
            else:
                logger.warn('%s has already append to %s.' % (intf, self.name))
        else:
            logger.error('Can\'t append %s to switch %s. % (intf, self.name)')
