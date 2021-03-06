#!/usr/bin/env python3

############################################################################
#                                                                          #
#  PyTCP - Python TCP/IP stack                                             #
#  Copyright (C) 2020  Sebastian Majewski                                  #
#                                                                          #
#  This program is free software: you can redistribute it and/or modify    #
#  it under the terms of the GNU General Public License as published by    #
#  the Free Software Foundation, either version 3 of the License, or       #
#  (at your option) any later version.                                     #
#                                                                          #
#  This program is distributed in the hope that it will be useful,         #
#  but WITHOUT ANY WARRANTY; without even the implied warranty of          #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the           #
#  GNU General Public License for more details.                            #
#                                                                          #
#  You should have received a copy of the GNU General Public License       #
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.  #
#                                                                          #
#  Author's email: ccie18643@gmail.com                                     #
#  Github repository: https://github.com/ccie18643/PyTCP                   #
#                                                                          #
############################################################################

##############################################################################################
#                                                                                            #
#  This program is a work in progress and it changes on daily basis due to new features      #
#  being implemented, changes being made to already implemented features, bug fixes, etc.    #
#  Therefore if the current version is not working as expected try to clone it again the     #
#  next day or shoot me an email describing the problem. Any input is appreciated. Also      #
#  keep in mind that some features may be implemented only partially (as needed for stack    #
#  operation) or they may be implemented in sub-optimal or not 100% RFC compliant way (due   #
#  to lack of time) or last but not least they may contain bug(s) that i didn't notice yet.  #
#                                                                                            #
##############################################################################################


#
# phrx_udp.py - packet handler for inbound UDP packets
#


from ipaddress import IPv4Address, IPv6Address

import loguru

import ps_icmpv4
import ps_icmpv6
import stack
from udp_metadata import UdpMetadata


def phrx_udp(self, ip_packet_rx, udp_packet_rx):
    """ Handle inbound UDP packets """

    self.logger.opt(ansi=True).info(f"<green>{udp_packet_rx.tracker}</green> - {udp_packet_rx}")

    # Validate UDP packet checksum
    if not udp_packet_rx.validate_cksum(ip_packet_rx.ip_pseudo_header):
        self.logger.debug(f"{udp_packet_rx.tracker} - UDP packet has invalid checksum, droping")
        return

    # Set universal names for src and dst IP addresses whether packet was delivered by IPv6 or IPv4 protocol
    ip_packet_rx.ip_dst = ip_packet_rx.ipv6_dst if ip_packet_rx.protocol == "IPv6" else ip_packet_rx.ipv4_dst
    ip_packet_rx.ip_src = ip_packet_rx.ipv6_src if ip_packet_rx.protocol == "IPv6" else ip_packet_rx.ipv4_src

    # Create UdpMetadata object and try to find matching UDP socket
    packet = UdpMetadata(
        local_ip_address=ip_packet_rx.ip_dst,
        local_port=udp_packet_rx.udp_dport,
        remote_ip_address=ip_packet_rx.ip_src,
        remote_port=udp_packet_rx.udp_sport,
        raw_data=udp_packet_rx.raw_data,
        tracker=udp_packet_rx.tracker,
    )

    for socket_id in packet.socket_id_patterns:
        socket = stack.udp_sockets.get(socket_id, None)
        if socket:
            loguru.logger.bind(object_name="socket.").debug(f"{packet.tracker} - Found matching listening socket {socket_id}")
            socket.process_packet(packet)
            return

    # Silently drop packet if it has all zero source IP address
    if ip_packet_rx.ip_src in {IPv4Address("0.0.0.0"), IPv6Address("::")}:
        self.logger.debug(
            f"Received UDP packet from {ip_packet_rx.ip_src}, port {udp_packet_rx.udp_sport} to {ip_packet_rx.ip_dst}, port {udp_packet_rx.udp_dport}, droping"
        )
        return

    # Respond with ICMPv4 Port Unreachable message if no matching socket has been found
    self.logger.debug(f"Received UDP packet from {ip_packet_rx.ip_src} to closed port {udp_packet_rx.udp_dport}, sending ICMPv4 Port Unreachable")

    if ip_packet_rx.protocol == "IPv6":
        self.phtx_icmpv6(
            ipv6_src=ip_packet_rx.ipv6_dst,
            ipv6_dst=ip_packet_rx.ipv6_src,
            icmpv6_type=ps_icmpv6.ICMP6_UNREACHABLE,
            icmpv6_code=ps_icmpv6.ICMP6_UNREACHABLE_PORT,
            icmpv6_un_raw_data=ip_packet_rx.get_raw_packet(),
            echo_tracker=udp_packet_rx.tracker,
        )

    if ip_packet_rx.protocol == "IPv4":
        self.phtx_icmpv4(
            ipv4_src=ip_packet_rx.ip_dst,
            ipv4_dst=ip_packet_rx.ip_src,
            icmpv4_type=ps_icmpv4.ICMP4_UNREACHABLE,
            icmpv4_code=ps_icmpv4.ICMP4_UNREACHABLE_PORT,
            icmpv4_un_raw_data=ip_packet_rx.get_raw_packet(),
            echo_tracker=udp_packet_rx.tracker,
        )

    return
