#! /usr/bin/python


class Intf(object):
    def __init__(self, name, ip=None, mac=None):
        self.name = name
        self.ip = ip
        self.mac = mac
