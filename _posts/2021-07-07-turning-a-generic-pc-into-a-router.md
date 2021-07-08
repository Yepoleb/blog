---
layout: post
title: Turning a generic PC into a router
date: 2021-07-07 20:56:00 +0200
---

### But why?

After messing around with DD-WRT and then OpenWrt on various devices for years, my dream for a long time has been to have just a generic PC with a gigabit network interface act as a router. This would get rid of a lot of issues I've had with consumer router devices:

* No updates of individual software components, only full system updates. Updating is annoying because it often needs to be manually and config compatibility is not guaranteed.
* Bad support for additional software. dpkg exists, but is nowhere near as polished and powerful as server distribution package managers.
* Incredibly slow to reboot. I have no idea about the reason for this, but every consumer router device has taken forever to get back online, no matter how powerful.
* Custom everything. Yes, it might be a Linux system, but everything needs to be configured using a custom webinterface or the config format of the embedded distribution.
* Most tools only offer basic functionality and are not as powerful as those on PCs.

I thought this doesn't need to be the case. We have 40€ single board computers that are supported by the same distributions we're used to, so why aren't 200€ routers?

### The hardware

My boyfriend also wanted some network storage, so we decided to merge both projects into one and got a cheap mini PC to serve as the general network PC. We already had a managed network switch with 802.1Q support (although used without special configuration) and a cheap 802.11ac router that served as an access point. My experience with ISP provided routers is that their wireless hardware is just bad at not dropping packets or even connections, so this was a necessary investment even earlier. The modem part is usually pretty good though, so this is the only thing they will be used for from now on.

### The process

While I will only document the final setup here, the actual deployment was done in multiple steps, each bringing back connectivity again so I could research the next steps and stream music to keep myself calm. These were roughly:

* Set up dnsmasq on the new machine and disable DHCP and DNS on the provider device.
* Set up IP forwarding and set the default route on my desktop PC to point to the new router.
* Create a VLAN interface and configure it as tagged in the switch UI. This becomes the LAN side interface and at this point the address that was previously assigned to the physical interface is assigned to this one.
* Create another VLAN interface to become the WAN side. The modem is put into new VLAN and a basic masquerade rule is added to iptables to allow traffic to continue.
* The modem is changed to bridge mode and the WAN side now needs to get its address using DHCP.
* Set up proper iptables rules.
* Bonus step: Set up stubby

### Switch configuration

This is very simple. Port 1 is the modem, port 2 the router. VLAN ID 1 is the default VLAN for all regular devices and ID 2 is used just to connect modem and router. The table below shows the 8 ports and their membership. T and U stand for tagged and untagged.

| ID | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 |
| -- | - | - | - | - | - | - | - | - |
|  1 |   | T | U | U | U | U | U | U | 
|  2 | U | T |   |   |   |   |   |   |

### sysctl

This line needs to be changed in `/etc/sysctl.conf` to allow IPv4 forwarding. IPv6 forwarding can be enabled here as well, but I only have IPv4 at home.

    net.ipv4.ip_forward=1

### networkd

These files are all placed in `/etc/systemd/network/`

#### loopback.network - loopback network configuration

    [Match]
    Name=lo

    [Network]
    Address=127.0.0.1/8
    Address=::1/128

#### wired.network - wired network configuration

    [Match]
    Name=enp2s0

    [Network]
    VLAN=lan
    VLAN=wan
    DNS=192.168.0.2

The VLAN entries are necessary to create the virtual interfaces on the device. DNS points to the LAN IP.

#### lan.netdev - LAN network device

    [NetDev]
    Name=lan
    Kind=vlan

    [VLAN]
    Id=1

#### lan.network - LAN network configuration

    [Match]
    Name=lan

    [Network]
    DHCP=no
    Address=192.168.0.2/24

DHCP needs to be turned off because this is where dnsmasq will be listening. The address of 192.168.0.2 is because while setting up everything I was still using the old router to stay connected, which was assigned 192.168.0.1.
    
#### wan.netdev - WAN network device

    [NetDev]
    Name=wan
    Kind=vlan

    [VLAN]
    Id=2

#### wan.network - WAN network configuration

    [Match]
    Name=wan

    [Network]
    DHCP=yes
    Address=192.168.100.2/24

    [DHCP]
    SendHostname=no
    UseDNS=no
    UseNTP=no
    UseRoutes=yes

This configuration actually has both DHCP, the actual public address, and a second static address for accessing the modem webinterface. `SendHostname=no` is to not leak hostnames to the outside, not for security, but so nobody can judge me for my naming choices. `UseDNS=no` is set because I will configure my own DNS upstream, `UseNTP=no` is not really necessary, but I don't want any autoconfiguration of NTP to happen. `UseRoutes=yes` will set the default route for the gateway, which is important because there is no other way to get the upstream route than DHCP.

### iptables

This is my rules script, which resides in `/usr/local/lib/iptables/rules.sh`. 

    #!/bin/sh
    # clear tables
    iptables -t filter -F
    iptables -t nat -F
    # default policy
    iptables -P INPUT ACCEPT
    iptables -P OUTPUT ACCEPT
    iptables -P FORWARD DROP
    # lan -> wan
    iptables -A INPUT -i lan -j ACCEPT
    iptables -A OUTPUT -o lan -j ACCEPT
    iptables -A FORWARD -i lan -o wan -j ACCEPT
    # wan -> lan
    iptables -A INPUT -i wan -j REJECT
    iptables -A OUTPUT -o wan -j ACCEPT
    iptables -A FORWARD -i wan -o lan -j REJECT
    # Allow established connections
    iptables -I INPUT -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    iptables -I FORWARD -m conntrack --ctstate RELATED,ESTABLISHED -j ACCEPT
    # masquerade lan
    iptables -t nat -A POSTROUTING -o wan -s 192.168.0.0/24 -j MASQUERADE
    # allow dhcp on wan
    iptables -I INPUT -i wan -p udp --dport 67:68 -j ACCEPT
    # allow icmp on wan
    iptables -I INPUT -i wan -p icmp -j ACCEPT
    # allow http/https
    iptables -I INPUT -i wan -p tcp --match multiport --dports 80,443 -j ACCEPT
    # allow ssh
    iptables -I INPUT -i wan -p tcp --dport 22 -j ACCEPT

It gets executed by this systemd service

    [Unit]
    Description=iptables configuration service
    After=network.target

    [Service]
    Type=oneshot
    ExecStart=/usr/local/lib/iptables/rules.sh
    RemainAfterExit=true

    [Install]
    WantedBy=multi-user.target

### dnsmasq

My dnsmasq configuration is split into a `base.conf` for general options and a `hosts.conf` for assigning static leases and placed into `/etc/dnsmasq.d/` instead of editing the main file.

#### base.conf

First of all, only listen on LAN and localhost. We don't want to be an unintentional open resolver.

    listen-address=192.168.0.2,127.0.0.1

This part is so client addresses can be queried using `<hostname>.lan`.

    local=/lan/
    domain=lan
    expand-hosts

Reading `/etc/hosts` is bad because dnsmasq shouldn't return 127.0.0.1 for the local hostname. Reading `/etc/resolv.conf` is also bad because I want the system to use the locally runnig DNS resolver, but the resolver itself would get stuck in an infinite loop.

    no-hosts
    no-resolv

Basic DHCP options like autoassign range and gateway address.
    
    dhcp-authoritative
    dhcp-range=192.168.0.10,192.168.0.100,12h
    dhcp-option=option:router,192.168.0.2

Stubby is running locally on port 5300 to do DNS over TLS translation.
    
    server=127.0.0.1#5300

Add a static entry for the device's own hostname

    address=/myhostname.lan/192.168.0.2

#### hosts.conf

I use this option to assign names to MAC addresses, which can then be resolved using DNS.

    dhcp-host=35:bf:75:60:1e:bd,Phone

It can also be used to assign both a name and an IP.

    dhcp-host=35:bf:75:60:1e:bd,Phone,192.168.0.101

### Stubby

The stubby config at `/etc/stubby/stubby.yml` is very simple, I only needed to change the listen address and pick one of the upstream resolvers.

    listen_addresses:
      - 127.0.0.1@5300
