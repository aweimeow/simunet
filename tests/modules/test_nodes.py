#! /usr/bin/python

import re
import pytest

from modules.node import Host, Switch
from utils.utils import Cmd


@pytest.fixture(scope="module")
def host():
    return Host('host_test')

@pytest.fixture(scope="module")
def switch():
    return Switch('switch_test')

@pytest.yield_fixture()
def run_test():
    Cmd('safe', 'docker stop host_test')
    Cmd('safe', 'docker rm host_test')
    Cmd('safe', 'ovs-vsctl del-br switch_test')
    yield

@pytest.mark.usefixtures('host')
class TestHostClass:
    def test_host_create(self, host):
        p = Cmd('shell', 'docker ps -a | grep host_test | cut -d " " -f 1')
        assert host.container_id[:12] == p.stdout.strip()

    def test_host_start(self, host):
        host.start()

        p = Cmd('shell', 'docker ps -a | grep host_test')
        assert re.match('.*Up Less than a second', p.stdout)

    def test_host_get_pid(self, host):
        p = Cmd('shell', 'ps -aux | grep %s' % host.pid)
        assert '/bin/bash' in p.stdout

    def test_host_stop(self, host):
        host.stop()

        p = Cmd('shell', 'docker ps -a | grep host_test')
        assert re.match('.*Exited \(\d+\) Less than a second ago', p.stdout)

    def test_host_destroy(self, host):
        assert host.status == 'stop' or host.status == 'create'
        host.destroy()

        p = Cmd('shell', 'docker ps -a | grep host_test')
        assert p.stdout.strip() == ''

@pytest.mark.usefixtures('switch')
class TestSwitchClass:
    def test_switch_create(self, switch):
        p = Cmd('safe', 'ovs-vsctl list-br')
        assert 'switch_test' in p.stdout

    def test_switch_destroy(self, switch):
        p = Cmd('safe', 'ovs-vsctl del-br switch_test')
        assert p.stderr == ''
        
        p = Cmd('safe', 'ovs-vsctl list-br')
        assert 'switch_test' not in p.stdout
        
