#! /usr/bin/python
from subprocess import Popen, PIPE


class Cmd:
    def __init__(self, mode, cmd):
        self.cmd = cmd
        if mode == 'safe':
            self.safeexec()
        elif mode == 'shell':
            self.shellexec()

    def safeexec(self):
        p = Popen(self.cmd.split(), stdout=PIPE, stderr=PIPE)
        self.stdout, self.stderr = p.communicate()

    def shellexec(self):
        p = Popen(self.cmd, stdout=PIPE, stderr=PIPE, shell=True)
        self.stdout, self.stderr = p.communicate()

