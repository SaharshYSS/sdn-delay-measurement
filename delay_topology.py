from mininet.net import Mininet
from mininet.node import RemoteController, OVSSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import time

def run():
    setLogLevel('info')
    net = Mininet(controller=RemoteController, switch=OVSSwitch, link=TCLink)

    c0 = net.addController('c0', controller=RemoteController,
                            ip='127.0.0.1', port=6633)

    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    h1 = net.addHost('h1', ip='10.0.0.1')
    h2 = net.addHost('h2', ip='10.0.0.2')
    h3 = net.addHost('h3', ip='10.0.0.3')
    h4 = net.addHost('h4', ip='10.0.0.4')

    # Different delays on each link
    net.addLink(h1, s1, delay='2ms',  bw=100)
    net.addLink(h2, s1, delay='5ms',  bw=100)
    net.addLink(h3, s2, delay='15ms', bw=100)
    net.addLink(h4, s2, delay='20ms', bw=100)
    net.addLink(s1, s2, delay='10ms', bw=100)

    net.start()
    info('\n*** Waiting for controller...\n')
    time.sleep(3)

    # ---- Automated Tests ----
    info('\n' + '='*55 + '\n')
    info('         NETWORK DELAY MEASUREMENT RESULTS\n')
    info('='*55 + '\n')

    tests = [
        ('h1', 'h2', 'h1->h2 same switch, low delay'),
        ('h1', 'h3', 'h1->h3 cross switch, medium delay'),
        ('h1', 'h4', 'h1->h4 cross switch, high delay'),
        ('h3', 'h4', 'h3->h4 same switch, high delay'),
    ]

    for src_name, dst_name, label in tests:
        src = net.get(src_name)
        dst = net.get(dst_name)
        info(f'\n[TEST] {label}\n')
        result = src.cmd(f'ping -c 10 -i 0.3 {dst.IP()}')
        for line in result.split('\n'):
            if 'rtt' in line or 'round-trip' in line:
                info(f'  {line}\n')

    info('\n' + '='*55 + '\n')
    info('*** Opening CLI for manual tests\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    run()
