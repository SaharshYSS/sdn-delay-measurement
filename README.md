# sdn-delay-measurement
# SDN Network Delay Measurement Tool
### Project 15 — SDN Mininet-Based Simulation

## Problem Statement
This project implements an SDN-based Network Delay Measurement Tool using Mininet and a POX OpenFlow controller. The tool measures and analyzes latency between hosts in a virtual network, records RTT (Round Trip Time) values, compares delays across different paths, and analyzes delay variations caused by different link configurations.

---

## Network Topology
```
h1 (10.0.0.1) --[2ms]--|
                        s1 --[10ms]-- s2 --[15ms]-- h3 (10.0.0.3)
h2 (10.0.0.2) --[5ms]--|             s2 --[20ms]-- h4 (10.0.0.4)
```

| Link | Delay | Bandwidth |
|------|-------|-----------|
| h1 ↔ s1 | 2 ms | 100 Mbps |
| h2 ↔ s1 | 5 ms | 100 Mbps |
| h3 ↔ s2 | 15 ms | 100 Mbps |
| h4 ↔ s2 | 20 ms | 100 Mbps |
| s1 ↔ s2 | 10 ms | 100 Mbps |

---

## Requirements
- Ubuntu Linux
- Mininet
- POX Controller
- Python 3.x
- Open vSwitch (installed with Mininet)

---

## Setup & Installation

### 1. Clone POX Controller
```bash
cd ~
git clone https://github.com/noxrepo/pox.git
```

### 2. Clone This Repository
```bash
git clone https://github.com/YOUR_USERNAME/sdn-delay-measurement.git
```

### 3. Copy Controller File into POX
```bash
cp sdn-delay-measurement/delay_controller.py ~/pox/pox/forwarding/
```

### 4. Copy Topology File to Home Directory
```bash
cp sdn-delay-measurement/delay_topology.py ~/
```

---

## How to Run

### Terminal 1 — Start the POX Controller
```bash
cd ~/pox
python3 pox.py forwarding.delay_controller
```
Leave this running.

### Terminal 2 — Start the Mininet Network
```bash
sudo mn -c
sudo python3 ~/delay_topology.py
```

---

## Expected Output

The topology automatically runs ping tests between all host pairs and prints RTT results:

```
=======================================================
         NETWORK DELAY MEASUREMENT RESULTS
=======================================================

[TEST] h1->h2 same switch, low delay
  rtt min/avg/max/mdev = 14.277/25.095/121.170/32.025 ms

[TEST] h1->h3 cross switch, medium delay
  rtt min/avg/max/mdev = 54.317/69.435/201.318/43.962 ms

[TEST] h1->h4 cross switch, high delay
  rtt min/avg/max/mdev = 64.664/76.644/180.237/34.531 ms

[TEST] h3->h4 same switch, high delay
  rtt min/avg/max/mdev = 70.205/82.378/190.064/35.895 ms
```

---

## Test Scenarios

### Scenario 1: Normal vs High Delay Path
```bash
# In mininet> prompt:
h1 ping -c 5 h2    # Low delay — same switch
h1 ping -c 5 h4    # High delay — cross switch
```
**Expected:** h1→h2 RTT much lower than h1→h4, proving delay measurement works correctly.

### Scenario 2: Normal vs Failure
```bash
# In mininet> prompt:
link s1 s2 down       # Simulate backbone link failure
h1 ping -c 3 h3       # Expected: 100% packet loss

link s1 s2 up         # Restore link
h1 ping -c 3 h3       # Expected: packets delivered successfully
```
**Expected:** Network correctly fails when link goes down and recovers when restored.

---

## Throughput Test (iperf)
```bash
# In mininet> prompt:
h2 iperf -s &
h1 iperf -c 10.0.0.2 -t 5
```
**Result:** ~94.6 Mbits/sec — close to the configured 100 Mbps link capacity.

---

## Flow Table Inspection
```bash
# In mininet> prompt:
sh ovs-ofctl dump-flows s1
sh ovs-ofctl dump-flows s2
```
Shows match-action flow rules installed by the controller in each switch.

---

## SDN Concepts Demonstrated
| Concept | Implementation |
|---------|---------------|
| Controller-Switch Interaction | POX receives packet_in, sends flow_mod to switches |
| Match-Action Flow Rules | Rules match on dst MAC + in_port, action outputs on learned port |
| MAC Learning | Controller builds MAC-to-port table dynamically |
| OpenFlow Protocol | POX and OVS communicate via OpenFlow 1.0 |
| Flow Timeout | Rules use idle_timeout=30s, expire after inactivity |
| Delay Measurement | TCLink adds per-link delays, ping captures end-to-end RTT |

---

## Proof of Execution

### 1. Automated RTT Delay Measurement Results
<img width="1179" height="683" alt="image" src="https://github.com/user-attachments/assets/33cd6a52-27c2-493a-98c5-ef4e99290a29" />

### 2. POX Controller — packet_in Events and Flow Rule Installation
<img width="1399" height="668" alt="image" src="https://github.com/user-attachments/assets/c6993e35-17aa-4ecd-9f3f-7027e16d6e4d" />

### 3. iperf Throughput Test and tcpdump Packet Capture
<img width="1440" height="686" alt="image" src="https://github.com/user-attachments/assets/343e856e-2aea-4ea0-9fe6-bdc23f79d4bf" />

### 4. Test Scenario — Normal vs Failure (Link Down and Recovery)
<img width="1347" height="690" alt="image" src="https://github.com/user-attachments/assets/a515015f-3f90-4f62-9956-8f4540e059fe" />

### 5. Test Scenario — Low Delay vs High Delay Path Comparison
<img width="1150" height="678" alt="image" src="https://github.com/user-attachments/assets/95774464-a64e-4b6f-a8ee-dec3f9042400" />



---

## Files
| File | Description |
|------|-------------|
| `delay_controller.py` | POX controller — handles packet_in, installs flow rules |
| `delay_topology.py` | Mininet topology — creates network with configured link delays |

---

## Tools Used
- **ping** — RTT latency measurement
- **iperf** — Throughput/bandwidth measurement  
- **tcpdump** — Packet capture at host level
- **ovs-ofctl** — Flow table inspection

---

## References
- Mininet: http://mininet.org/
- POX Controller: https://github.com/noxrepo/pox
- OpenFlow Specification: https://opennetworking.org/
- B. Lantz, B. Heller, N. McKeown, "A Network in a Laptop", ACM HotNets 2010
