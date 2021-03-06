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
# stack.py - module holds references to the stack components and global configuration paameters
#


from ipaddress import IPv4Interface, IPv6Interface

# TAP interface name stack should bind itself to
interface = b"tap7"

# Support for IPv6 and IPv4, at least one should be anabled
ipv6_support = True
ipv4_support = True

# Unicast MAC addresses assigned to stack, currently there is not any kind of duplicate MAC detection performed
mac_address_candidate = ["02:00:00:77:77:77"]

# IPv6 address auto configuration is implemented using EUI64 addressing and ICMPv6 Router Advertisement messages
ipv6_address_autoconfig_enabled = True

# There is no IPv6 routing implemented yet so we do not care about the IPv6 default gateway address
ipv6_address_candidate = [
    # IPv6Interface("FE80::7/64"),
    # IPv6Interface("FE80::77/64"),
    # IPv6Interface("FE80::777/64"),
    # IPv6Interface("FE80::7777/64"),
    IPv6Interface("2007::7/64"),
    # ipv6_eui64(STACK_MAC_ADDRESS, IPv6Network("2007::/64")),
]

# IPv4 DHCP based address configuration
ipv4_address_dhcp_enabled = True

# Static IPv4 adrsses may to be configured here (they will still be subject to ARP Probe/Announcement mechanism)
# Each entry is a tuple interface address/prefix length and second is defaut gateway for this subnet
# Basic routing is implmented and each subnet can have its own gateway
ipv4_address_candidate = [
    ("192.168.9.7/24", "192.168.9.1"),
    # ("192.168.9.77/24", "192.168.9.1"),
    # ("DUPA", "192.168.9.1"),  # test invalid address format
    # ("192.168.9.99/24", "DUPA"),  # test invalid gateway format
    # ("192.168.9.77/24", "192.168.9.1"),  # test duplicate address
    # ("192.168.9.170/24", "10.0.0.1"),  # test invalid gateway
    # ("192.168.9.171/24", "192.168.9.0"),  # test invalid gateway
    # ("192.168.9.172/24", "192.168.9.172"),  # test invalid gateway
    # ("192.168.9.173/24", "192.168.9.255"),  # test invalid gateway
    # ("192.168.9.0/24", "192.168.9.1"),  # test invalid address
    # ("192.168.9.255/24", "192.168.9.1"),  # test invalid address
    # ("0.0.0.0/0", None),  # test invalid address
    # ("192.168.9.102/24", None),  # test no gateway
    # ("172.16.17.7/24", "172.16.17.1"),
    # ("10.10.10.7/24", "10.10.10.1"),
]

mtu = 1500  # TAP interface MTU

local_tcp_mss = 1460  # Maximum segment peer can send to us
local_tcp_win = 65535  # Maximum amount of data peer can send to us without confirmation

# Test services and clients, for detailed configuation of each reffer to pytcp.py and respective service/client file
# Those are being used for testing various stack components are therefore their 'default' funcionality may be altered fro specific tst needs
# Eg. TCP daytime service generates large amount of text data used to verify TCP protocol funcionality
service_udp_echo = True
service_udp_discard = True
service_udp_daytime = True
service_tcp_echo = True
service_tcp_discard = True
service_tcp_daytime = True
client_tcp_echo = False
client_icmpv4_echo = True

# References to stack components
rx_ring = None
tx_ring = None
arp_cache = None
icmpv6_nd_cache = None
packet_handler = None
stack_timer = None

# Stack 'global variables'
tcp_sessions = {}
udp_sockets = {}
