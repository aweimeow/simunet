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

    def __init__(self, name, os='ubuntu:14.04'):
        """default value:
        name: h1 (str)
        os: ubuntu:14.04 (str)
        """

        self.os = os
        self.name = name
        self.intf = {}
        self.gateway = None
        self.status = None
        self.create()


    def set_gateway(self, gateway):
        self.gateway = gateway

    def network_config(self):
        """ Configuration for container's IP, mac and gateway """

        for name, intf in self.intf.iteritems():
            cmd = ("docker exec {} ifconfig {} {}").format(
                   self.name, name, intf.ip)
            Cmd('safe', cmd)

            if intf.mac:
               cmd = ("docker exec {} ifconfig {} hw ether {}").format(
                       self.name, name, intf.mac)

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
        
        self.intf = {}

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
