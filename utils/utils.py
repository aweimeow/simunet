#! /usr/bin/python
from subprocess import Popen, PIPE


class cmd:
    def __init__(self, cmd):
        self.cmd = cmd

    def exec(self):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        self.stdout, self.stderr = p.communicate()

    def shellexec(self):
        p = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
        self.stdout, self.stderr = p.communicate()

