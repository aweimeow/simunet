#! /usr/bin/python
# -*- encoding: utf-8 -*-

from simunet.modules.intf import Intf
from simunet.utils.utils import Cmd, Logger

logger = Logger('node.py', 'WARNING')


class Host(object):
    """
    A docker based container, use to simulate network host
    """

    def __init__(self, name, os='ubuntu:14.04'):
        """default value:
        name: h1 (str)
        os: ubuntu:14.04 (str)
        """

        self.__os = os
        self.__name = name
        self.__status = None
        self.intf = {}
        self.create()
        self.start()

    # os, name, status is readonly private variable
    # it is not recommended to modify it after initialize
    @property
    def os(self):
        return self.__os

    @property
    def name(self):
        return self.__name

    @property
    def status(self):
        return self.__status

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
            self.__status = 'create'

    def start(self):
        """ Start the container """

        if self.__status == 'start':
            logger.warn('%s has been started.' % self.name)
            return

        if self.__status == 'destroy':
            logger.error('%s has been destroyed.' % self.name)
            return

        # Send start command
        cmd = "docker start {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.__status = 'start'

        # get docker's pid
        cmd = "docker inspect --format '{{.State.Pid}}' %s" % self.name
        p = Cmd('safe', cmd)
        self.pid = int(p.stdout.strip().replace("'", ""))

    def stop(self):
        """ Stop the container """

        if self.__status == 'stop':
            logger.error('%s has been stoped.' % self.name)
            return

        cmd = "docker stop {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.__status = 'stop'

    def destroy(self):
        """ Remove this Container """

        if self.__status == 'destroy':
            logger.error('%s has been destroyed.' % self.name)
            return

        if self.__status == 'start':
            logger.warn('%s can\'t destroy: Stop container first' % self.name)
            return

        cmd = "docker rm {}".format(self.container_id)
        p = Cmd('safe', cmd)
        self.__status = 'destroy'


class Switch(object):
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
            logger.error(p.stderr)

    def network_config(self):
        for name, intf in self.intf.iteritems():
            p = Cmd('safe', 'ifconfig %s up' % intf.name)

            if p.stderr:
                logger.error('%s config error: %s' % self.name, p.stderr)
            
