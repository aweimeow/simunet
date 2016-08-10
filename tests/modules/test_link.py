#! /usr/bin/python

import re
import pytest

from simunet.modules.node import Host, Switch
from simunet.modules.link import Link, TCLink
from simunet.utils.utils import Cmd


@pytest.fixture(scope="module")
def h1():
    return Host('h1')

@pytest.fixture(scope="module")
def h2():
    return Host('h2')

@pytest.fixture(scope="module")
def h3():
    return Host('h3')

@pytest.fixture(scope="module")
def h4():
    return Host('h4')

@pytest.fixture(scope="module")
def sw1():
    return Switch('sw1')

@pytest.fixture(scope="module")
def sw2():
    return Switch('sw2')

dockers = ['h1', 'h2', 'h3', 'h4']
ovs = ['sw1', 'sw2']

@pytest.yield_fixture(autouse=True)
def run_test():
    for docker in dockers:
        Cmd('safe', 'docker stop %s' % docker)
        Cmd('safe', 'docker rm %s' % docker)
    for switch in ovs:
        Cmd('safe', 'ovs-vsctl del-br %s' % switch)
    yield
    for docker in dockers:
        Cmd('safe', 'docker stop %s' % docker)
        Cmd('safe', 'docker rm %s' % docker)
    for switch in ovs:
        Cmd('safe', 'ovs-vsctl del-br %s' % switch)

@pytest.mark.usefixtures('h1', 'h2', 'sw1')
class TestLinkClass:

    def test_host_switch_link_create(self, h1, h2, sw1):
        link1 = Link(h1, sw1)

        p = Cmd('safe', 'docker exec h1 ifconfig %s' % link1.intf1.name)
        assert link1.intf1.name in p.stdout
        p = Cmd('safe', 'ovs-vsctl show')
        assert link1.intf2.name in p.stdout

        link2 = Link(h2, sw1)
        
        p = Cmd('safe', 'docker exec h2 ifconfig %s' % link2.intf1.name)
        assert link2.intf1.name in p.stdout
        p = Cmd('safe', 'ovs-vsctl show')
        assert link2.intf2.name in p.stdout

        link1.intf1.ip = '10.0.0.1/24'
        link2.intf1.ip = '10.0.0.2/24'   

        h1.network_config()
        h2.network_config()

        sw1.network_config()

        p = Cmd('safe', 'docker exec h1 ping 10.0.0.2 -c 1')
        assert '64 bytes from 10.0.0.2' in p.stdout

        p = Cmd('safe', 'docker exec h2 ping 10.0.0.1 -c 1')
        assert '64 bytes from 10.0.0.1' in p.stdout

@pytest.mark.usefixtures('h3', 'h4', 'sw2')
class TestTCLinkClass:

    def test_tclink_create(self, h3, h4, sw2):
        delay = 500
        bw=1
        link1 = TCLink(h3, sw2, bw=1, delay=delay, loss=10)
        link2 = TCLink(h4, sw2, bw=10, delay=0, loss=10)
        link1.tc_active()

        link1.intf1.ip = '10.0.0.3/24'
        link2.intf1.ip = '10.0.0.4/24'

        h3.network_config()
        h4.network_config()
        sw2.network_config()

        # Check delay
        p = Cmd('safe', 'docker exec h3 ping 10.0.0.4 -c 4')
        check_stdout = p.stdout.split('\n')[2]
        assert re.match('.*time=%s ms' % delay, check_stdout) is not None

