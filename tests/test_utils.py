#! /usr/bin/python

import pytest
from random import random

from utils.utils import Cmd


class TestCmdClass:
    def test_safeexec_stdout(self):
        cmd = Cmd('safe', 'echo TEST')
        assert cmd.stdout == 'TEST\n'

    def test_safeexec_stderr(self):
        rand_name = hex(hash(random() * random()))
        cmd = Cmd('safe', 'cat %s' % rand_name)
        assert cmd.stderr == 'cat: %s: No such file or directory\n' % rand_name
