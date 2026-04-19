from pox.core import core
from pox.lib.util import dpidToStr
import pox.openflow.libopenflow_01 as of

log = core.getLogger()

class DelayController(object):
    def __init__(self, connection):
        self.connection = connection
        self.mac_to_port = {}
        connection.addListeners(self)
        log.info("Switch %s connected", dpidToStr(connection.dpid))

    def _handle_PacketIn(self, event):
        packet = event.parsed
        if not packet.parsed:
            return

        dpid = event.connection.dpid
        in_port = event.port

        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][packet.src] = in_port

        if packet.dst in self.mac_to_port[dpid]:
            out_port = self.mac_to_port[dpid][packet.dst]
            log.info("Switch %s: %s -> %s via port %s",
                     dpidToStr(dpid), packet.src, packet.dst, out_port)

            # Install flow rule (match + action)
            msg = of.ofp_flow_mod()
            msg.match.dl_dst = packet.dst
            msg.match.in_port = in_port
            msg.actions.append(of.ofp_action_output(port=out_port))
            msg.idle_timeout = 30
            msg.hard_timeout = 0
            event.connection.send(msg)

            # Send current packet
            msg2 = of.ofp_packet_out()
            msg2.data = event.ofp
            msg2.actions.append(of.ofp_action_output(port=out_port))
            event.connection.send(msg2)
        else:
            # Flood if destination unknown
            log.info("Switch %s: unknown dst %s, flooding", dpidToStr(dpid), packet.dst)
            msg = of.ofp_packet_out()
            msg.data = event.ofp
            msg.actions.append(of.ofp_action_output(port=of.OFPP_FLOOD))
            event.connection.send(msg)

def launch():
    def start_switch(event):
        DelayController(event.connection)
    core.openflow.addListenerByName("ConnectionUp", start_switch)
    log.info("Delay Measurement Controller launched")
