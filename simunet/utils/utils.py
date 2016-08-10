#! /usr/bin/python

import os
import logging
import coloredlogs

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

class Logger:
    def __init__(self, module_name, level):
        os.environ['COLOREDLOGS_LOG_FORMAT'] = (
            '%(asctime)s %(name)s %(levelname)s %(message)s'
            )
        os.environ['COLOREDLOGS_LEVEL_STYLES'] = (
            'info=white; verbos=white; debug=green;'
            'warning=yellow;error=red;critical=red,bold;'
            )
        self.logger = logging.getLogger(module_name)
        coloredlogs.install(level=level)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warn(self, msg):
        self.logger.warn(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

