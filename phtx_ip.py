#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack simulation version 0.1 - 2020, Sebastian Majewski
phtx_ip.py - packet handler for outbound IP packets

"""

import struct
import socket
import random

import ps_ip
import ps_ether

MTU = 1500


def phtx_ip(self, child_packet, ip_dst):
    """ Handle outbound IP packets """

    if ps_ether.ETHER_HEADER_LEN + ps_ip.IP_HEADER_LEN + len(child_packet.raw_packet) <= MTU:
        ip_packet_tx = ps_ip.IpPacket(hdr_src=self.stack_ip_address, hdr_dst=ip_dst, child_packet=child_packet)

        self.logger.debug(f"{ip_packet_tx.tracker} - {ip_packet_tx}")
        self.phtx_ether(child_packet=ip_packet_tx)

    else:
        if child_packet.protocol == "ICMP":
            ip_proto = ps_ip.IP_PROTO_ICMP
            raw_data = child_packet.get_raw_packet()

        if child_packet.protocol == "UDP":
            ip_proto = ps_ip.IP_PROTO_UDP
            raw_data = child_packet.get_raw_packet(
                struct.pack(
                    "! 4s 4s BBH",
                    socket.inet_aton(self.stack_ip_address),
                    socket.inet_aton(ip_dst),
                    0,
                    ps_ip.IP_PROTO_UDP,
                    len(child_packet.raw_packet),
                )
            )

        if child_packet.protocol == "TCP":
            ip_proto = ps_ip.IP_PROTO_TCP
            raw_data = child_packet.get_raw_packet(
                struct.pack(
                    "! 4s 4s BBH",
                    socket.inet_aton(self.stack_ip_address),
                    socket.inet_aton(ip_dst),
                    0,
                    ps_ip.IP_PROTO_UDP,
                    len(child_packet.raw_packet),
                )
            )

        self.logger.debug("Packet exceedes available MTU, IP fragmentation needed...")
        raw_data_mtu = (MTU - ps_ether.ETHER_HEADER_LEN - ps_ip.IP_HEADER_LEN) & 0b1111111111111000
        raw_data_fragments = [raw_data[_ : raw_data_mtu + _] for _ in range(0, len(raw_data), raw_data_mtu)]

        n = 0
        offset = 0
        ip_id = random.randint(0, 65535)

        for raw_data_fragment in raw_data_fragments:
            ip_packet_tx = ps_ip.IpPacket(
                hdr_src=self.stack_ip_address,
                hdr_dst=ip_dst,
                hdr_proto=ip_proto,
                hdr_id=ip_id,
                hdr_frag_mf=True if n < len(raw_data_fragments) - 1 else False,
                hdr_frag_offset=offset,
                raw_data=raw_data_fragment,
            )
            n += 1
            offset += len(raw_data_fragment)

            self.logger.debug(f"{ip_packet_tx.tracker} - {ip_packet_tx}")
            self.phtx_ether(child_packet=ip_packet_tx)