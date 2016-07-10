#! /usr/bin/python
# -*- encoding: utf-8 -*-

import logging

from utils.utils import Cmd, Logger

logger = Logger('node.py', 'WARNING')


class Host:
    """
    A docker based container, use to simulate network host
    """

    def __init__(self, os, node_id, name, ip, mac):
        """default value:
        os: ubuntu:14.04 (str)
        node_id: 1 (int)
        name: h1 (str)
        ip: 10.0.0.1/24 (str)
        mac: AA:BB:CC:DD:EE:FF (str)
        """

        self.os = os
        self.node_id = node_id
        self.name = name
        self.ip = ip
        self.mac = mac
        self.gateway = None
        self.status = None
        self.create()

    def network_config(self):
        """ Configuration for container's IP, mac and gateway """

        cmd = ("docker exec %s ifconfig %s-eth0 %s hw ether %s").format(
               self.name, self.name, self.ip, self.mac)
        Cmd('safe', cmd)
        if self.gateway:
            cmd = ("docker exec %s route add default gw %s").format(
                   self.name, self.gateway)
            Cmd('safe', cmd)

    def set_gateway(self, gateway):
        self.gateway = gateway

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

        cmd = "docker start {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.status = 'start'


    def stop(self):
        """ Stop the container """

        if self.status == 'stop':
            logger.error('%s has been stoped' % self.name)

        cmd = "docker stop {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.status = 'stop'

