#!/usr/bin/env python3

"""

PyTCP, Python TCP/IP stack simulation version 0.1 - 2020, Sebastian Majewski
phrx_udp.py - packet handler for inbound UDP packets

"""

from udp_socket import UdpSocket

import ps_icmp


def phrx_udp(self, ip_packet_rx, udp_packet_rx):
    """ Handle inbound UDP packets """

    self.logger.opt(ansi=True).info(f"<green>{udp_packet_rx.tracker}</green> - {udp_packet_rx}")

    # Check if incoming packet matches any listening socket
    socket = UdpSocket.match_listening(
        local_ip_address=ip_packet_rx.hdr_dst,
        local_port=udp_packet_rx.hdr_dport,
        tracker=udp_packet_rx.tracker,
    )
    if socket:
        socket.enqueue(
            src_ip_address=ip_packet_rx.hdr_src,
            src_port=udp_packet_rx.hdr_sport,
            raw_data=udp_packet_rx.raw_data,
        )
        return

    # In case incoming packet did't mach any listening port respond with ICMP Port Unreachable message
    self.logger.debug(f"Received UDP packet from {ip_packet_rx.hdr_src} to closed port {udp_packet_rx.hdr_dport}, sending ICMP Port Unreachable")

    self.phtx_icmp(
        ip_dst=ip_packet_rx.hdr_src,
        icmp_type=ps_icmp.ICMP_UNREACHABLE,
        icmp_code=ps_icmp.ICMP_UNREACHABLE_PORT,
        icmp_msg_data=ip_packet_rx.get_raw_packet(),
        echo_tracker=udp_packet_rx.tracker,
    )