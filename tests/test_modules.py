#! /usr/bin/python

import re
import pytest

from modules.node import Host
from utils.utils import Cmd


@pytest.fixture(scope="module")
def host():
    return Host('ubuntu:14.04', 1, 'h1',
                '10.0.0.1', '00:AA:BB:CC:DD:EE')

@pytest.mark.usefixtures('host')
class TestHostClass:
    def test_host_create(self, host):
        p = Cmd('shell', 'docker ps -a | grep h1 | cut -d " " -f 1')
        assert host.container_id[:12] == p.stdout.strip()

    def test_host_start(self, host):
        host.start()
        p = Cmd('shell', 'docker ps -a | grep h1')
        assert re.match('.*Up Less than a second', p.stdout)

    def test_host_stop(self, host):
        host.stop()
        p = Cmd('shell', 'docker ps -a | grep h1')
        print p.stdout
        assert re.match('.*Exited \(0\) Less than a second ago', p.stdout)
