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

    def test_shellexec_stdout(self):
        cmd = Cmd('shell', 'echo 1\n2\n3\n | grep 1')
        assert cmd.stdout == '1\n'

    def test_shellexec_stderr(self):
        cmd = Cmd('shell', 'echo 1 | grep')
        err = ("Usage: grep [OPTION]... PATTERN [FILE]...\n"
               "Try 'grep --help' for more information.\n"
               "sh: echo: I/O error\n")
        assert cmd.stderr == err
