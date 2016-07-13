#! /usr/bin/python

import re
import pytest

from modules.node import Host, Switch
from modules.link import Link
from utils.utils import Cmd


@pytest.fixture(scope="module")
def h1():
    return Host('h1')

@pytest.fixture(scope="module")
def h2():
    return Host('h2')

@pytest.fixture(scope="module")
def sw1():
    return Switch('sw1')

@pytest.yield_fixture(autouse=True)
def run_test():
    Cmd('safe', 'docker stop h1')
    Cmd('safe', 'docker stop h2')
    Cmd('safe', 'docker rm h1')
    Cmd('safe', 'docker rm h2')
    Cmd('safe', 'ovs-vsctl del-br sw1')
    yield
    Cmd('safe', 'docker stop h1')
    Cmd('safe', 'docker stop h2')
    Cmd('safe', 'docker rm h1')
    Cmd('safe', 'docker rm h2')
    Cmd('safe', 'ovs-vsctl del-br sw1')

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

