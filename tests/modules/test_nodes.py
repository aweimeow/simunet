#! /usr/bin/python

import re
import pytest

from modules.node import Host, Switch
from utils.utils import Cmd


@pytest.fixture(scope="module")
def host():
    return Host('h1', '10.0.0.1', mac='00:AA:BB:CC:DD:EE')

@pytest.fixture(scope="module")
def switch():
    return Switch('sw1')

@pytest.mark.usefixtures('host')
class TestHostClass:
    def test_host_create(self, host):
        p = Cmd('shell', 'docker ps -a | grep h1 | cut -d " " -f 1')
        assert host.container_id[:12] == p.stdout.strip()

    def test_host_start(self, host):
        host.start()

        p = Cmd('shell', 'docker ps -a | grep h1')
        assert re.match('.*Up Less than a second', p.stdout)

    def test_host_get_pid(self, host):
        p = Cmd('shell', 'ps -aux | grep %s' % host.pid)
        assert '/bin/bash' in p.stdout

    def test_host_stop(self, host):
        host.stop()

        p = Cmd('shell', 'docker ps -a | grep h1')
        assert re.match('.*Exited \(\d+\) Less than a second ago', p.stdout)

    def test_host_destroy(self, host):
        assert host.status == 'stop' or host.status == 'create'
        host.destroy()

        p = Cmd('shell', 'docker ps -a | grep h1')
        assert p.stdout.strip() == ''

@pytest.mark.usefixtures('switch')
class TestSwitchClass:
    def test_switch_create(self, switch):
        p = Cmd('safe', 'ovs-vsctl list-br')
        assert 'sw1' in p.stdout

    def test_switch_destroy(self, switch):
        p = Cmd('safe', 'ovs-vsctl del-br sw1')
        assert p.stderr == ''
        
        p = Cmd('safe', 'ovs-vsctl list-br')
        assert 'sw1' not in p.stdout
        
